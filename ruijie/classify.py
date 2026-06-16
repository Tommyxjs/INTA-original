from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MANUAL_INDEX = BASE_DIR / "manual_index.json"
DEFAULT_CLASSIFY_TEMPLATE = BASE_DIR / "classify_template.txt"
DEFAULT_MATCH_TEMPLATE = BASE_DIR / "match_template.txt"

TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_./-]+")
JSON_BLOCK_PATTERN = re.compile(r"\{.*\}", re.DOTALL)


def load_text(path: Path, description: str) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing {description}: {path}")
    return path.read_text(encoding="utf-8")


def load_manual_index(path: Path) -> Dict[str, Any]:
    text = load_text(path, "manual index")
    return json.loads(text)


def load_configuration(config_file: Optional[Path], inline_text: Optional[str]) -> str:
    if config_file and inline_text:
        raise ValueError("Provide either --config-file or --config-text, not both.")
    if config_file:
        return load_text(config_file, "configuration")
    if inline_text:
        return inline_text
    raise ValueError("Configuration input missing. Use --config-file or --config-text.")


def split_commands(configuration: str) -> List[str]:
    return [line.strip() for line in configuration.splitlines() if line.strip()]


def build_client(api_key: Optional[str], base_url: Optional[str]) -> OpenAI:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set. Pass via env or --api-key.")
    url = base_url or os.getenv("OPENAI_BASE_URL")
    return OpenAI(api_key=key, base_url=url)


def call_model(client: OpenAI, model: str, prompt: str, temperature: float = 0.0) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


def extract_json(content: str) -> Dict[str, Any]:
    snippet = content.strip()
    if snippet.startswith("```"):
        snippet = "\n".join(
            line for line in snippet.splitlines() if not line.strip().startswith("```")
        )
    try:
        return json.loads(snippet)
    except json.JSONDecodeError:
        match = JSON_BLOCK_PATTERN.search(snippet)
        if not match:
            raise
        return json.loads(match.group())


def tokenize(text: str) -> List[str]:
    return [token for token in TOKEN_PATTERN.findall(text.lower()) if token]


def filter_candidates(target_command: str, candidates: Sequence[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    cmd_tokens = set(tokenize(target_command))
    if not cmd_tokens:
        return list(candidates), []

    kept: List[Dict[str, Any]] = []
    removed: List[Dict[str, Any]] = []
    for entry in candidates:
        cand_tokens = set(tokenize(entry.get("name", "")))
        if cmd_tokens & cand_tokens:
            kept.append(entry)
        else:
            removed.append(entry)
    return kept, removed


def format_candidate_lines(candidates: Sequence[Dict[str, Any]]) -> str:
    lines = []
    for idx, entry in enumerate(candidates, start=1):
        description = entry.get("description") or ""
        description = description.replace("\n", " ").strip()
        if not description:
            description = "No description available"
        lines.append(f"{idx}. {entry.get('name', '').strip()} :: {description}")
    return "\n".join(lines)


def run_classification(
    client: OpenAI,
    template: str,
    configuration: str,
    command: str,
    model: str,
    temperature: float,
) -> Tuple[Dict[str, Any], str]:
    prompt = (
        f"{template}\n\n"
        f"## CONFIGURATION\n{configuration.strip()}\n\n"
        f"## TARGET_COMMAND\n{command}\n"
    )
    raw = call_model(client, model, prompt, temperature)
    parsed = extract_json(raw)
    return parsed, raw


def run_matching(
    client: OpenAI,
    template: str,
    src_device: str,
    primary_section: Optional[str],
    secondary_section: str,
    command: str,
    candidates: Sequence[Dict[str, Any]],
    model: str,
    temperature: float,
) -> Tuple[Dict[str, Any], str]:
    candidate_block = format_candidate_lines(candidates)
    prompt = template.format(
        src_device=src_device,
        primary_section=primary_section or "Unknown",
        secondary_section=secondary_section,
        target_command=command,
        candidate_commands=candidate_block,
    )
    raw = call_model(client, model, prompt, temperature)
    parsed = extract_json(raw)
    return parsed, raw


def ensure_candidate_limit(candidates: List[Dict[str, Any]], limit: Optional[int]) -> Tuple[List[Dict[str, Any]], int]:
    if not limit or len(candidates) <= limit:
        return candidates, 0
    return candidates[:limit], len(candidates) - limit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify Ruijie commands and match manual commands.")
    parser.add_argument("--config-file", type=Path, default=None, help="Path to configuration snippet text file.")
    parser.add_argument("--config-text", type=str, default=None, help="Configuration snippet provided inline.")
    parser.add_argument("--src-device", type=str, default="Ruijie")
    parser.add_argument("--manual-index", type=Path, default=DEFAULT_MANUAL_INDEX)
    parser.add_argument("--classify-template", type=Path, default=DEFAULT_CLASSIFY_TEMPLATE)
    parser.add_argument("--match-template", type=Path, default=DEFAULT_MATCH_TEMPLATE)
    parser.add_argument("--classify-model", type=str, default="gpt-4o")
    parser.add_argument("--match-model", type=str, default="gpt-4o")
    parser.add_argument("--classify-temperature", type=float, default=0.0)
    parser.add_argument("--match-temperature", type=float, default=0.0)
    parser.add_argument("--max-candidates", type=int, default=25)
    parser.add_argument("--output-json", type=Path, default=None, help="Write aggregated JSON results to this path.")
    parser.add_argument("--api-key", type=str, default=None, help="OpenAI-compatible API key.")
    parser.add_argument("--base-url", type=str, default=None, help="Custom base URL for the OpenAI-compatible endpoint.")
    args = parser.parse_args()
    return args


def main() -> None:
    args = parse_args()
    try:
        configuration = load_configuration(args.config_file, args.config_text)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(2)

    commands = split_commands(configuration)
    if not commands:
        print("[WARN] No commands extracted from configuration.")
        return

    classify_template = load_text(args.classify_template, "classify template")
    match_template = load_text(args.match_template, "match template")
    manual_index = load_manual_index(args.manual_index)
    client = build_client(args.api_key, args.base_url)

    aggregated: List[Dict[str, Any]] = []

    for command in commands:
        print("\n====== COMMAND ======")
        print(command)

        try:
            classification, raw_classify = run_classification(
                client,
                classify_template,
                configuration,
                command,
                args.classify_model,
                args.classify_temperature,
            )
        except Exception as exc:
            print(f"[ERROR] Classification failed: {exc}")
            aggregated.append(
                {
                    "command": command,
                    "classification_error": str(exc),
                }
            )
            continue

        secondary = classification.get("Secondary_Section")
        primary = classification.get("Primary_Section")
        matched_flag = classification.get("Matched")
        confidence = classification.get("Confidence")
        print(f"Section => {secondary} (Primary: {primary}, Confidence: {confidence}, Matched: {matched_flag})")

        manual_entry = manual_index.get(secondary or "") if secondary else None
        candidates = manual_entry.get("commands", []) if manual_entry else []
        kept, removed = filter_candidates(command, candidates)
        kept, truncated = ensure_candidate_limit(kept, args.max_candidates)
        print(
            f"Candidates => total:{len(candidates)} kept:{len(kept)} removed(no keyword):{len(removed)} truncated:{truncated}"
        )

        match_payload: Dict[str, Any]
        raw_match: Optional[str] = None
        if not secondary:
            match_payload = {"status": "skipped", "reason": "No secondary section returned"}
        elif not kept:
            match_payload = {"status": "skipped", "reason": "No candidates share keywords"}
        else:
            try:
                match_payload, raw_match = run_matching(
                    client,
                    match_template,
                    args.src_device,
                    manual_entry.get("primary") if manual_entry else primary,
                    secondary,
                    command,
                    kept,
                    args.match_model,
                    args.match_temperature,
                )
                print(f"Best match => {match_payload.get('Best_Candidate')} (Confidence: {match_payload.get('Confidence')})")
            except Exception as exc:
                print(f"[ERROR] Matching failed: {exc}")
                match_payload = {"status": "error", "reason": str(exc)}

        aggregated.append(
            {
                "command": command,
                "classification": classification,
                "classification_raw": raw_classify,
                "secondary_section": secondary,
                "manual_candidates_total": len(candidates),
                "manual_candidates_removed": len(removed),
                "manual_candidates_kept": len(kept),
                "candidates_truncated": truncated,
                "matching": match_payload,
                "matching_raw": raw_match,
            }
        )

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(aggregated, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nResults written to {args.output_json}")


if __name__ == "__main__":
    main()
