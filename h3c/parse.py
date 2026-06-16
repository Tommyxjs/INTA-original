import pdfplumber
import re
import json
from pypdf import PdfReader
from ruijie.classify_copy import run_ruijie_classification
from openai import OpenAI
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

client = OpenAI(
    api_key="sk-TlwpjduGIDx8uLVDQwBMPcWu4ndg27usjtYw7ZE2cKZR4al7",
    base_url="https://www.yunqiaoai.top/v1",
)
all_translated_fragments = []
# configuration = """
# router bgp 6
# bgp bestpath as-path multipath-relax
# bgp log-neighbor-changes
# bgp graceful-restart restart-time 120
# bgp graceful-restart stalepath-time 360
# bgp graceful-restart
# neighbor 192.168.2.65 remote-as 2000
# address-family ipv4
# maximum-paths ebgp 64
# network 10.51.6.0 mask 255.255.255.0
# neighbor 192.168.2.65 activate
# exit-address-family
# """
configuration = """
router bgp 6
 bgp bestpath as-path multipath-relax
 bgp log-neighbor-changes
 bgp graceful-restart restart-time 120
 bgp graceful-restart stalepath-time 360
 bgp graceful-restart
 neighbor 192.168.2.65 remote-as 2000
 neighbor 192.168.2.67 remote-as 2000
 neighbor 192.168.2.69 remote-as 2000
 neighbor 192.168.2.71 remote-as 2000
 neighbor 192.168.2.73 remote-as 2000
 neighbor 192.168.2.75 remote-as 2000
 neighbor 192.168.2.77 remote-as 2000
 neighbor 192.168.2.79 remote-as 2000
 neighbor 192.168.2.81 remote-as 2000
 neighbor 192.168.2.83 remote-as 2000
 neighbor 192.168.2.85 remote-as 2000
 neighbor 192.168.2.87 remote-as 2000
 neighbor 192.168.2.89 remote-as 2000
 neighbor 192.168.2.91 remote-as 2000
 neighbor 192.168.2.93 remote-as 2000
 neighbor 192.168.2.95 remote-as 2000
 neighbor 192.168.2.97 remote-as 2000
 neighbor 192.168.2.99 remote-as 2000
 neighbor 192.168.2.101 remote-as 2000
 neighbor 192.168.2.103 remote-as 2000
 neighbor 192.168.2.105 remote-as 2000
 neighbor 192.168.2.107 remote-as 2000
 neighbor 192.168.2.109 remote-as 2000
 neighbor 192.168.2.111 remote-as 2000
 neighbor 192.168.2.113 remote-as 2000
 neighbor 192.168.2.115 remote-as 2000
 neighbor 192.168.2.117 remote-as 2000
 neighbor 192.168.2.119 remote-as 2000
 neighbor 192.168.2.121 remote-as 2000
 neighbor 192.168.2.123 remote-as 2000
 neighbor 192.168.2.125 remote-as 2000
 neighbor 192.168.2.127 remote-as 2000
 address-family ipv4
  maximum-paths ebgp 64
  network 10.51.6.0 mask 255.255.255.0
  neighbor 192.168.2.65 activate
  neighbor 192.168.2.67 activate
  neighbor 192.168.2.69 activate
  neighbor 192.168.2.71 activate
  neighbor 192.168.2.73 activate
  neighbor 192.168.2.75 activate
  neighbor 192.168.2.77 activate
  neighbor 192.168.2.79 activate
  neighbor 192.168.2.81 activate
  neighbor 192.168.2.83 activate
  neighbor 192.168.2.85 activate
  neighbor 192.168.2.87 activate
  neighbor 192.168.2.89 activate
  neighbor 192.168.2.91 activate
  neighbor 192.168.2.93 activate
  neighbor 192.168.2.95 activate
  neighbor 192.168.2.97 activate
  neighbor 192.168.2.99 activate
  neighbor 192.168.2.101 activate
  neighbor 192.168.2.103 activate
  neighbor 192.168.2.105 activate
  neighbor 192.168.2.107 activate
  neighbor 192.168.2.109 activate
  neighbor 192.168.2.111 activate
  neighbor 192.168.2.113 activate
  neighbor 192.168.2.115 activate
  neighbor 192.168.2.117 activate
  neighbor 192.168.2.119 activate
  neighbor 192.168.2.121 activate
  neighbor 192.168.2.123 activate
  neighbor 192.168.2.125 activate
  neighbor 192.168.2.127 activate
  exit-address-family
"""
ruijie_outputs = run_ruijie_classification(configuration)

pdf_path = BASE_DIR / "h3c_config_manual.pdf"

reader = PdfReader(pdf_path)

toc_pages = []
toc_items = []

# ================= 提取页面文本 =================
with pdfplumber.open(pdf_path) as pdf:

    pages = pdf.pages
    total_pages = len(pages)

    in_toc = False

    for i in range(total_pages):

        page_index = i + 1
        page = pages[i]

        text = page.extract_text()

        if text:
            lines = [l.strip() for l in text.split("\n") if l.strip()]
        else:
            lines = []

        if not lines:
            continue

        first_line = lines[0]

        print(f"检查第 {page_index} 页: {first_line}")

        # ================= 目录开始 =================第一行是目录两个字
        if not in_toc and first_line.replace(" ", "") == "目录":
            in_toc = True
            toc_pages.append(page_index)
            continue

        # ================= 目录结束 =================第一行是1 xxx
        if in_toc:

            if first_line == "1":
                print(f"目录结束于第 {page_index-1} 页")
                in_toc = False
                continue

            toc_pages.append(page_index)

print("\n目录页:", toc_pages)


# ================= 提取 PDF 链接 =================
def extract_links(reader, page_index):

    page = reader.pages[page_index]

    links = []

    if "/Annots" not in page:
        return links

    for annot in page["/Annots"]:

        obj = annot.get_object()

        if obj.get("/Subtype") != "/Link":
            continue

        rect = obj.get("/Rect")

        dest = None

        if "/Dest" in obj:
            dest = obj["/Dest"]

        elif "/A" in obj and obj["/A"].get("/S") == "/GoTo":
            dest = obj["/A"].get("/D")

        links.append({
            "rect": rect,
            "dest": dest
        })

    return links


# ================= 提取目录内容 =================
with pdfplumber.open(pdf_path) as pdf:

    for page_index in toc_pages:

        page = pdf.pages[page_index-1]

        text = page.extract_text()

        if text:
            lines = [l.strip() for l in text.split("\n") if l.strip()]
        else:
            lines = []

        page_links = extract_links(reader, page_index-1)

        height = page.height

        for line in lines:

            if line.replace(" ", "") == "目录":
                continue

            # 匹配目录结构
            if not re.match(r"^\d+(\.\d+)*\s+", line):
                continue

            link_dest = None

            for link in page_links:

                x0, y0, x1, y1 = link["rect"]

                bbox = (x0, height-y1, x1, height-y0)

                txt = page.within_bbox(bbox).extract_text()

                if txt and line[:15] in txt:
                    link_dest = link["dest"]
                    break

            toc_items.append({
                "title": line,
                "dest": link_dest,
                "page": page_index
            })


# ================= 输出结构化目录 =================
toc_tree = []
current_root_title = None

for item in toc_items:
    raw = item["title"]

    m = re.match(r"^(\d+(?:\.\d+)*)\s+(.+)$", raw)
    if not m:
        continue

    number = m.group(1)
    title = m.group(2).strip()

    # 清掉点线和页码
    clean_title = re.sub(
        r'\s*[·.]{2,}\s*\d+(?:\s*\d+)*(?:\s*-\s*\d+(?:\s*\d+)*)?\s*$',
        '',
        title
    ).strip()

    # 一级编号，如 1 / 2 / 3
    level = number.count(".") + 1

    # 如果是一级标题，把自己当作 root
    if level == 1:
        current_root_title = clean_title

    toc_tree.append({
        "root_title": current_root_title.strip() if current_root_title else "",
        "number": number.strip(),
        "title": clean_title.strip(),
        "dest": item["dest"]
    })



print("\n========== H3C TOC ==========")

for t in toc_tree:
    print(f"{t['number']} {t['title']}")

print("\n目录总数:", len(toc_tree))

toc_index = {}
for item in toc_tree:
    key = (item["root_title"], item["number"])
    if key in toc_index:
        print(f"⚠️ 重复目录键: {key}")
    toc_index[key] = item


def extract_section_doc(number, dest, max_pages=8):
    if dest is None:
        return ""

    target_page = None
    for i, page in enumerate(reader.pages):
        try:
            if page.indirect_reference == dest[0]:
                target_page = i
                break
        except Exception:
            continue

    if target_page is None:
        return ""

    section_lines = []
    found_start = False
    current_level = None

    section_pattern = re.compile(r'^(\d+(?:\.\d+)*)\s+')

    with pdfplumber.open(pdf_path) as pdf:
        end_page = min(target_page + max_pages, len(pdf.pages))

        for page_num in range(target_page, end_page):
            text = pdf.pages[page_num].extract_text()
            if not text:
                continue

            for line in text.split("\n"):
                line = line.strip()
                if not line:
                    continue

                m = section_pattern.match(line)
                if m:
                    section_no = m.group(1)
                    level = len(section_no.split("."))

                    if not found_start:
                        if section_no != number:
                            continue
                        found_start = True
                        current_level = level
                    else:
                        if level <= current_level:
                            return "\n".join(section_lines)

                if found_start:
                    section_lines.append(line)

    return "\n".join(section_lines)

def get_selected_section_docs(select_toc):
    results = []

    for item in select_toc:
        root_title = str(item.get("root_title", "")).strip()
        root_title = re.sub(r"^[【\[]\s*|\s*[】\]]$", "", root_title).strip()
        number = item.get("number", "").strip()
        subtitle = item.get("subtitle", "")
        confidence = item.get("confidence", "")
        reasoning = item.get("reasoning", "")

        if not root_title or not number:
            print(f"⚠️ 缺少 root_title 或 number: {item}")
            continue

        toc_item = toc_index.get((root_title, number))
        if not toc_item:
            print(f"⚠️ 未找到目录项: root_title={root_title}, number={number}")
            continue

        doc_text = extract_section_doc(number, toc_item.get("dest"))

        results.append({
            "root_title": root_title,
            "number": number,
            "subtitle": subtitle,
            "title": toc_item.get("title", ""),
            "confidence": confidence,
            "reasoning": reasoning,
            "doc": doc_text
        })

    return results



# # ================= 保存 JSON =================
# with open("h3c_config_toc.json","w",encoding="utf-8") as f:
#     json.dump(toc_tree,f,ensure_ascii=False,indent=2)

# print("\n✅ 目录已保存: h3c_config_toc.json")

# level12_toc = []

# for item in toc_tree:

#     number = item["number"]

#     level = number.count(".") + 1

#     if level <= 2:
#         level12_toc.append(item)

# print("\n===== 一级 + 二级目录 =====\n")

# for item in level12_toc:

#     print(f"{item['number']} {item['title']}")


# =========================================================
# 使用LLM对h3c的配置手册进行筛选
# =========================================================
for ruijie_output in ruijie_outputs:

    # 1 读取 prompt 模板
    with open(BASE_DIR / "select_h3c_config_template.txt", "r", encoding="utf-8") as f:
        select_h3c_config_template_template = f.read()

    # 2 准备填充变量
    src_device = "Ruijie"
    tgt_device = "H3C"
    config_manuals = ruijie_output["config_manual"]
    command_manuals = ruijie_output["command_manual"]
    # suffix = ""

    grouped_toc_lines = []
    last_root = None

    for t in toc_tree:
        if t["root_title"] != last_root:
            grouped_toc_lines.append(f"\n【{t['root_title']}】")
            last_root = t["root_title"]

        grouped_toc_lines.append(f"{t['number']} {t['title']}")

    config_toc_text = "\n".join(grouped_toc_lines)

    # 3 构造 Prompt
    select_prompt = (
        select_h3c_config_template_template
        .replace("{src_device}", src_device)
        .replace("{tgt_device}", tgt_device)
        .replace("{src_config}", ruijie_output["target_config"])
        .replace("{src_config_manuals}", "\n".join(ruijie_output["config_manual"]))
        .replace("{src_cmd_manuals}", "\n".join(ruijie_output["command_manual"]))
        .replace("{CONFIG_TOC_TEXT}", config_toc_text)
    )

    print("\n========== CONFIG SELECT PROMPT ==========")
    print(select_prompt)   # 防止打印太长
    translate_config_manual_input = ""

    # =========================================================
    # Step: 调用大模型
    # =========================================================

    try:

        response = client.chat.completions.create(
            model="gpt-5.4",
            messages=[
                {
                    "role": "user",
                    "content": select_prompt
                }
            ],
            temperature=0
        )

        select_result = response.choices[0].message.content

        print("\n========== LLM RAW RESULT ==========")
        print(select_result)

        # =====================================================
        # Step: 解析 JSON
        # =====================================================

        try:

            json_str = re.search(r"\[.*\]", select_result, re.S).group()

            select_toc = json.loads(json_str)
    
            print("\n========== PARSED FRAGMENTS ==========")
            print(select_toc)
            selected_docs = get_selected_section_docs(select_toc)

            print("\n========== SELECTED DOCS ==========")
            for item in selected_docs:
                print(f"\n### 【{item['root_title']}】 {item['number']} {item['title']}")
                print(item["doc"])
                print("-" * 80)
            translate_config_manual_input = "\n".join(item["doc"] for item in selected_docs)

        except Exception as e:
            print("JSON 解析失败:", e)

    except Exception as e:
        print("LLM 调用失败:", e)

    # =========================================================
    # 使用LLM进行翻译wiz manual
    # =========================================================
    print("\n========== TRANSLATE PROMPT 使用LLM进行翻译wiz manual==========")
    # 1 读取 prompt 模板
    with open(BASE_DIR / "translate_template.txt", "r", encoding="utf-8") as f:
        translate_template = f.read()

    # 2 准备填充变量
    src_device = "Ruijie"
    tgt_device = "H3C"
    config_manuals = ruijie_output["config_manual"]
    command_manuals = ruijie_output["command_manual"]
    # suffix = ""

    # 3 构造 Prompt
    translate_prompt = (
        translate_template
        .replace("{src_device}", src_device)
        .replace("{tgt_device}", tgt_device)
        .replace("{src_config}", ruijie_output["ruijie_config"])
        .replace("{src_config_manuals}", "\n".join(ruijie_output["config_manual"]))
        .replace("{src_cmd_manuals}", "\n".join(ruijie_output["command_manual"]))
        .replace("{tgt_config_manuals}", translate_config_manual_input)
    )

    print("\n========== CONFIG DIVIDE PROMPT ==========")
    print(translate_prompt)   # 防止打印太长


    # =========================================================
    # Step: 调用大模型
    # =========================================================

    try:

        response = client.chat.completions.create(
            model="gpt-5.4",
            messages=[
                {
                    "role": "user",
                    "content": translate_prompt
                }
            ],
            temperature=0
        )

        translate_result = response.choices[0].message.content

        print("\n========== LLM RAW RESULT ==========")
        print(translate_result)

        # =====================================================
        # Step: 解析 JSON
        # =====================================================

        try:
            code_match = re.search(r"```(?:\w+)?\n(.*?)```", translate_result, re.S)
            if code_match:
                raw_text = code_match.group(1).strip()
            else:
                raw_text = translate_result.strip()
            fragments = [line.rstrip() for line in raw_text.splitlines() if line.strip()]
    
            print("\n========== PARSED FRAGMENTS ==========")
            print(fragments)
            all_translated_fragments.append(fragments)
        except Exception as e:
            print("JSON 解析失败:", e)

    except Exception as e:
        print("LLM 调用失败:", e)
final_config = "\n".join(
    "\n".join(item)
    for item in all_translated_fragments
)
print(final_config)
