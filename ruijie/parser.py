from __future__ import annotations

import argparse
import json
import re
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Tuple

import pdfplumber

MANUAL_STRUCTURE = OrderedDict({
    "基础配置": [
        "命令行界面",
        "零配置自动部署",
        "基础管理",
        "RBAC",
        "Line",
        "文件系统管理",
        "USB",
        "系统日志",
        "软件升级",
        "Time Range",
        "转发表模式管理",
        "管理板冗余",
        "模块热插拔",
        "重启进程",
        "Python",
        "软件授权管理",
        "Hungtask 命令",
        "TCAM 模式管理命令",
        "ECC 修复命令",
    ],
    "设备管理": ["告警管理"],
    "虚拟化": ["VSU"],
    "接口": ["以太网接口", "链路聚合口"],
    "以太网交换": [
        "MAC 地址",
        "端口回环",
        "VLAN",
        "MAC VLAN",
        "Protocol VLAN",
        "Private VLAN",
        "Super VLAN",
        "GVRP",
        "QinQ",
        "MSTP",
        "ERPS",
        "LLDP",
    ],
    "IP业务": [
        "ARP",
        "IPv4 基础",
        "DHCP",
        "DHCP 客户端",
        "DHCP Snooping",
        "DNS",
        "IPv6 基础",
        "DHCPv6",
        "DHCPv6 客户端",
        "隧道",
        "TCP",
        "IP 快转",
    ],
    "IP路由": [
        "IP 路由基础",
        "静态路由",
        "RIP",
        "RIPng",
        "OSPFv2",
        "OSPFv3",
        "IS-IS",
        "BGP",
        "VRF",
        "路由策略",
        "策略路由",
        "密钥",
    ],
    "组播": [
        "IPv4 组播路由管理",
        "IGMP",
        "PIM-SM",
        "PIM-DM",
        "IGMP Snooping",
        "MSDP",
        "IPv6 组播路由管理",
        "MLD",
        "PIM-SMv6",
        "MLD Snooping",
    ],
    "MPLS": ["MPLS 基础", "MPLS L3VPN", "MPLS RAS(可靠性)", "Segment Routing"],
    "ACL和QoS": ["ACL", "QoS", "队列缓存管理"],
    "安全": [
        "AAA",
        "RADIUS",
        "TACACS",
        "SCC(安全控制中心)",
        "Password Policy",
        "SSH",
        "CPP(CPU 保护策略)",
        "NFPP(网络基础保护策略)",
        "风暴控制",
        "uRPF(单播反向路径转发)",
        "DoS 保护",
        "安全日志审计",
    ],
    "可靠性": [
        "REUP",
        "RLDP",
        "DLDP",
        "M-LAG",
        "VRRP",
        "VRRP Plus",
        "BFD",
        "Track",
        "路由接口震荡抑制",
        "背板口监控",
        "HAM",
        "DAG",
    ],
    "网管与监控": [
        "网络连通性检测",
        "一键收集",
        "镜像",
        "报文捕获",
        "sFlow",
        "IPFIX",
        "查看设备重启原因",
        "NTP",
        "SNTP",
        "FTP 服务器",
        "FTP 客户端",
        "TFTP 服务器",
        "TFTP 客户端",
        "SNMP",
        "RMON",
        "NETCONF",
        "gRPC",
        "OpenFlow",
        "智能嵌入式管理器",
        "IFA",
        "IDS",
        "智能监控",
        "智能硬件诊断",
        "HOTKEY",
    ],
    "数据中心": ["VXLAN", "PFC", "RDMA"],
})

SECONDARY_TO_PRIMARY = {
    secondary: primary
    for primary, secondaries in MANUAL_STRUCTURE.items()
    for secondary in secondaries
}

SECTION_HEADER_PATTERN = re.compile(r"^命令参考\s+(.+)$")
TABLE_HEADER_PATTERN = re.compile(r"^命令\s+作用$")
NUMBERED_SUBSECTION_PATTERN = re.compile(r"^(\d+(?:\.\d+)*)\s+(.+)$")


def normalize_line(line: str) -> str:
    return " ".join(line.strip().split())


def extract_ascii_prefix(text: str) -> Tuple[str, str]:
    if not text:
        return "", ""

    for idx, ch in enumerate(text):
        if ord(ch) > 127:
            return text[:idx].strip(), text[idx:].strip()
    return text.strip(), ""


def register_command(section_bucket, section_name, command_name, description, page):
    if not command_name:
        return
    bucket = section_bucket.setdefault(section_name, {
        "primary": SECONDARY_TO_PRIMARY.get(section_name),
        "first_page": None,
        "commands": [],
        "_seen": {},
    })
    if bucket["first_page"] is None:
        bucket["first_page"] = page
    seen = bucket["_seen"]
    if command_name in seen:
        existing = seen[command_name]
        if description and not existing.get("description"):
            existing["description"] = description
        return

    entry = {
        "name": command_name,
        "description": description,
        "page": page,
    }
    seen[command_name] = entry
    bucket["commands"].append(entry)


def finalize_bucket(section_bucket):
    for data in section_bucket.values():
        data.pop("_seen", None)
        if data.get("commands"):
            data["commands"] = sorted(
                data["commands"],
                key=lambda item: (item["page"], item["name"].lower()),
            )
    return section_bucket


def parse_manual(pdf_path: Path):
    section_bucket: Dict[str, Dict] = {
        section: {
            "primary": SECONDARY_TO_PRIMARY[section],
            "first_page": None,
            "commands": [],
            "_seen": {},
        }
        for section in SECONDARY_TO_PRIMARY
    }

    pages_as_text = {}
    current_section = None
    capture_table = False

    with pdfplumber.open(str(pdf_path)) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            raw_text = page.extract_text() or ""
            lines = [normalize_line(line) for line in raw_text.split("\n") if line.strip()]
            pages_as_text[idx] = lines

            for line in lines:
                header_match = SECTION_HEADER_PATTERN.match(line)
                if header_match:
                    candidate = header_match.group(1).strip()
                    if candidate in section_bucket:
                        current_section = candidate
                        capture_table = False
                        bucket = section_bucket[current_section]
                        if bucket["first_page"] is None:
                            bucket["first_page"] = idx
                        continue

                if not current_section:
                    continue

                if TABLE_HEADER_PATTERN.match(line):
                    capture_table = True
                    continue

                if capture_table:
                    command_name, description = extract_ascii_prefix(line)
                    if not description:
                        capture_table = False
                        continue
                    register_command(section_bucket, current_section, command_name, description, idx)
                    continue

                numbered_match = NUMBERED_SUBSECTION_PATTERN.match(line)
                if numbered_match:
                    candidate_command = numbered_match.group(2).strip()
                    ascii_prefix, _ = extract_ascii_prefix(candidate_command)
                    register_command(section_bucket, current_section, ascii_prefix or candidate_command, "", idx)

    return finalize_bucket(section_bucket), pages_as_text


def write_plain_text(pages_as_text: Dict[int, List[str]], output_txt: Path) -> None:
    with output_txt.open("w", encoding="utf-8") as handle:
        for page_number, lines in pages_as_text.items():
            handle.write(f"============ PAGE_{page_number} ============\n")
            for line in lines:
                handle.write(f"{line}\n")
            handle.write("\n")


def write_json_index(section_bucket: Dict[str, Dict], output_json: Path) -> None:
    serializable = OrderedDict(sorted(section_bucket.items(), key=lambda item: item[0]))
    with output_json.open("w", encoding="utf-8") as handle:
        json.dump(serializable, handle, ensure_ascii=False, indent=2)


def parse_args():
    parser = argparse.ArgumentParser(description="Parse Ruijie command manual into structured JSON.")
    parser.add_argument(
        "--pdf",
        type=Path,
        default=Path(__file__).with_name("ruijie_command_manual.pdf"),
        help="Path to the Ruijie PDF manual.",
    )
    parser.add_argument(
        "--text-output",
        type=Path,
        default=Path(__file__).with_name("ruijie_command_manual.txt"),
        help="Destination for the flattened text export.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path(__file__).with_name("manual_index.json"),
        help="Destination for the structured command index in JSON format.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    section_bucket, pages_as_text = parse_manual(args.pdf)
    write_plain_text(pages_as_text, args.text_output)
    write_json_index(section_bucket, args.json_output)
    print(
        f"✅ Parsed manual '{args.pdf.name}' -> text: {args.text_output.name}, index: {args.json_output.name}"
    )


if __name__ == "__main__":
    main()
