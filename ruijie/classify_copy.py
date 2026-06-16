from openai import OpenAI
from datetime import datetime


client = OpenAI(
    api_key="sk-TlwpjduGIDx8uLVDQwBMPcWu4ndg27usjtYw7ZE2cKZR4al7",
    base_url="https://www.yunqiaoai.top/v1",
)


import pdfplumber
import re
import json
from pypdf import PdfReader
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
command_pdf_path = BASE_DIR / "ruijie_command_manual.pdf"
command_output_txt = BASE_DIR / "ruijie_command_manual.txt"
config_pdf_path = BASE_DIR / "ruijie_config_manual.pdf"
config_output_txt = BASE_DIR / "ruijie_config_manual.txt"
def run_ruijie_classification(configuration):
    # 用于存储最终结果的字典
    command_pdf_dict = {}
    config_pdf_dict = {}

    command_title_index = {}  # 存储每个二级标题的起始页码
    config_title_index = {}

    ruijie_output = []

    command_reader = PdfReader(command_pdf_path)
    config_reader = PdfReader(config_pdf_path)


    command_category = {
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
            "ECC 修复命令"],
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
            "LLDP"],
        "IP业务": ["ARP",
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
                "IP 快转"],
        "IP路由": ["IP 路由基础",
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
                "密钥"],
        "组播": ["IPv4 组播路由管理",
            "IGMP",
            "PIM-SM",
            "PIM-DM",
            "IGMP Snooping",
            "MSDP",
            "IPv6 组播路由管理",
            "MLD",
            "PIM-SMv6",
            "MLD Snooping"],
        "MPLS": ["MPLS 基础",
                "MPLS L3VPN",
                "MPLS RAS(可靠性)",
                "Segment Routing"],
        "ACL和QoS": ["ACL",
                    "QoS",
                    "队列缓存管理"],
        "安全": ["AAA",
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
            "安全日志审计"],
        "可靠性": ["REUP",
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
                "DAG"],
        "网管与监控": ["网络连通性检测",
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
                "HOTKEY"],
        "数据中心": ["VXLAN",
                "PFC",
                "RDMA"]}

    config_category = {
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
            "Uboot 操作",
            "Rboot 操作",
            "Time Range",
            "转发表模式管理",
            "管理板冗余",
            "模块热插拔",
            "重启进程",
            "Python",
            "软件授权管理",
            "Hungtask 命令",
            "TCAM 模式管理命令",
            "ECC 修复命令"],
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
            "LLDP"],
        "IP业务": ["ARP",
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
                "IP 快转"],
        "IP路由": ["IP 路由基础",
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
                "密钥"],
        "组播": ["组播基础",
            "IPv4 组播路由管理",
            "IGMP",
            "PIM-SM",
            "PIM-DM",
            "IGMP Snooping",
            "IPv6 组播路由管理",
            "MLD",
            "PIM-SMv6",
            "MLD Snooping"],
        "MPLS": ["MPLS 基础",
                "MPLS L3VPN",
                "MPLS RAS(可靠性)",
                "Segment Routing"],
        "ACL和QoS": ["ACL",
                    "QoS",
                    "队列缓存管理"],
        "安全": ["AAA",
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
            "安全日志审计"],
        "可靠性": ["REUP",
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
                "DAG"],
        "网管与监控": ["网络连通性检测",
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
                "HOTKEY"],
        "数据中心": ["VXLAN",
                "PFC"]}

    #从目录中解析跳转链接
    def extract_config_links(config_reader, page_index):
        page = config_reader.pages[page_index]

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

    #处理config manual中的目录和跳转信息
    def build_config_toc_text_and_index(toc_items):
        """
        返回两部分：
        1) 格式化后的目录字符串（保留编号，去掉多余点/页码）
        2) 目录条目索引（编号 -> 条目），便于后续按编号定位
        """
        toc_text = ""
        toc_index = []

        for item in toc_items:
            raw = item["title"]

            # 匹配「编号 + 标题」，去掉末尾点/页码
            m = re.match(r'^(\d+(?:\.\d+)*)\s+(.+?)(?:\.{2,}\s*\d+)?$', raw)
            if not m:
                continue

            number = m.group(1)
            title = m.group(2).strip()

            level = number.count(".") + 1
            indent = "  " * (level - 1)

            toc_text += f"{indent}- {number} {title}\n"

            toc_index.append({
                "number": number,
                "title": title,
                "subtitle": item["subtitle"],
                "dest": item["dest"]
            })

        return toc_text, toc_index

    def extract_config_doc(num, dest, max_pages=5):
        """
        num: 章节子目录
        dest: 目录里解析出的 /GoTo 目标
        max_pages: 最多向后扫描的页数，防止一次性读完整本书
        """
        if dest is None:
            return ""

        # 1) 找到对应页
        target_page = None
        for i, page in enumerate(config_reader.pages):
            if page.indirect_reference == dest[0]:
                target_page = i
                break
        if target_page is None:
            return ""

        section_lines = []
        found_start = False
        current_level = None

        section_pattern_config = re.compile(r'^(\d+(?:\.\d+)*)\s+')

        with pdfplumber.open(config_pdf_path) as pdf:
            end_page = min(target_page + max_pages, len(pdf.pages))

            for page_num in range(target_page, end_page):
                text = pdf.pages[page_num].extract_text()
                if not text:
                    continue

                for line in text.split("\n"):
                    # 匹配“1.6.1 标题”这类行
                    m = section_pattern_config.match(line)
                    if m:
                        section_no = m.group(1)
                        if section_no != num and current_level == None:
                            continue
                        level = len(section_no.split("."))

                        if not found_start:
                            found_start = True
                            current_level = level
                        else:
                            # 遇到同级或更高层级的标题，停止
                            if level <= current_level:
                                return "\n".join(section_lines)

                    if found_start:
                        section_lines.append(line)

        return "\n".join(section_lines)

    #打开命令手册PDF，提取目录信息并构建索引
    with pdfplumber.open(command_pdf_path) as pdf:
        command_pages = pdf.pages
        for page_index, page in enumerate(command_pages, start=1):
            text = page.extract_text()

            if text:
                # 按行切分，并去掉空行
                lines = [line.strip() for line in text.split("\n") if line.strip()]
            else:
                lines = []

            if lines:  # 如果页面有内容
                first_line = lines[0]  # 获取第一页的第一行
                # 使用正则表达式匹配两种格式
                print(f"检查第 {page_index} 页的第一行: {first_line}")

                # # 第一种情况：匹配 "命令参考+-+内容" 格式
                # match1 = re.match(r'^命令参考-(.+)$', first_line)
                # if match1:
                #     extracted_content = match1.group(1)
                #     if extracted_content in command_category:
                #         command_category[extracted_content]["begin_page"] = page_index
                #         result_dict[current_key] = []  # 初始化key对应的value列表
                #     # print(f"在第 {page_index} 页找到第一种匹配项: {extracted_content}")
                # else:
                # 第二种情况：匹配 "命令参考 内容" 格式
                match2 = re.match(r'^命令参考\s+(.+)$', first_line)
                if match2:
                    extracted_content = match2.group(1)
                    found = False
                    for substtles in command_category.values():
                        if extracted_content in substtles:
                            if extracted_content not in command_title_index:
                                command_title_index[extracted_content] = {
                                    "begin_page": page_index}
                            found = True
                            break
                    # print(f"在第 {page_index} 页找到第二种匹配项: {extracted_content}")

            command_pdf_dict[f"page_{page_index}"] = lines

    # ========== 格式化写入 TXT ==========
    with open(command_output_txt, "w", encoding="utf-8") as f:
        for page, lines in command_pdf_dict.items():
            f.write(f"{'=' * 12} {page.upper()} {'=' * 12}\n")
            for line in lines:
                f.write(line + "\n")
            f.write("\n")

    print("✅ ruijie_command_manual.pdf 已成功转换为结构化文本")
    print("--------------------------------")
    #补全错误匹配的subtitle目录页码（根据实际文档内容人工补全）
    for subtitles in command_category.values():
        for subtitle in subtitles:
            if subtitle in command_title_index:
                print(
                    f"'{subtitle}': starts at page {command_title_index[subtitle]['begin_page']}")
            else:
                if subtitle == "转发表模式管理":
                    command_title_index[subtitle] = {'begin_page': 374}
                elif subtitle == "Hungtask 命令":
                    command_title_index[subtitle] = {'begin_page': 449}
                elif subtitle == "TCAM 模式管理命令":
                    command_title_index[subtitle] = {'begin_page': 456}
                elif subtitle == "ECC 修复命令":
                    command_title_index[subtitle] = {'begin_page': 459}
                elif subtitle == "MAC 地址":
                    command_title_index[subtitle] = {'begin_page': 694}
                elif subtitle == "端口回环":
                    command_title_index[subtitle] = {'begin_page': 735}
                elif subtitle == "IPv4 基础":
                    command_title_index[subtitle] = {'begin_page': 1078}
                elif subtitle == "DHCP 客户端":
                    command_title_index[subtitle] = {'begin_page': 1214}
                elif subtitle == "IPv6 基础":
                    command_title_index[subtitle] = {'begin_page': 1268}
                elif subtitle == "DHCPv6 客户端":
                    command_title_index[subtitle] = {'begin_page': 1395}
                elif subtitle == "IP 快转":
                    command_title_index[subtitle] = {'begin_page': 1437}
                elif subtitle == "IP 路由基础":
                    command_title_index[subtitle] = {'begin_page': 1499}
                elif subtitle == "IPv4 组播路由管理":
                    command_title_index[subtitle] = {'begin_page': 2587}
                elif subtitle == "IPv6 组播路由管理":
                    command_title_index[subtitle] = {'begin_page': 2824}
                elif subtitle == "MPLS 基础":
                    command_title_index[subtitle] = {'begin_page': 2965}
                elif subtitle == "MPLS RAS(可靠性)":
                    command_title_index[subtitle] = {'begin_page': 3058}
                elif subtitle == "Segment Routing":
                    command_title_index[subtitle] = {'begin_page': 3067}
                elif subtitle == "队列缓存管理":
                    command_title_index[subtitle] = {'begin_page': 3378}
                elif subtitle == "CPP(CPU 保护策略)":
                    command_title_index[subtitle] = {'begin_page': 3629}
                elif subtitle == "uRPF(单播反向路径转发)":
                    command_title_index[subtitle] = {'begin_page': 3825}
                elif subtitle == "DoS 保护":
                    command_title_index[subtitle] = {'begin_page': 3835}
                elif subtitle == "FTP 服务器":
                    command_title_index[subtitle] = {'begin_page': 4199}
                elif subtitle == "FTP 客户端":
                    command_title_index[subtitle] = {'begin_page': 4221}
                elif subtitle == "TFTP 服务器":
                    command_title_index[subtitle] = {'begin_page': 4228}
                elif subtitle == "TFTP 客户端":
                    command_title_index[subtitle] = {'begin_page': 4234}
                elif subtitle == "IFA":
                    command_title_index[subtitle] = {'begin_page': 4444}
                elif subtitle == "PFC":
                    command_title_index[subtitle] = {'begin_page': 4650}
                else:
                    print(f"'{subtitle}': not found in the document")
                print(
                    f"'{subtitle}': starts at page {command_title_index[subtitle]['begin_page']}")

    # ================= 提取“命令-作用”表格（严格以表头为准，支持跨页） =================
    # 根据索引index的字典提取所有的命令-作用表格
    command_table = {}
    # 匹配末尾中文“作用描述”
    desc_pattern = re.compile(r'([\u4e00-\u9fa5].*)$')

    # 匹配整行罗马数字页脚（i / ii / iii / iv ...）
    roman_pattern = re.compile(r'^[ivxlcdm]+$', re.IGNORECASE)

    #从目录中解析跳转链接
    def extract_command_links(command_reader, page_index):
        page = command_reader.pages[page_index]

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

    section_pattern = re.compile(r'^\d+\.\d+\s+')
    # 从目录链接中提取对应内容
    def extract_command_doc(dest):

        if dest is None:
            return ""

        # 1 找到目标页
        target_page = None

        for i, page in enumerate(command_reader.pages):
            if page.indirect_reference == dest[0]:
                target_page = i
                break

        if target_page is None:
            return ""

        section_lines = []
        found_start = False

        with pdfplumber.open(command_pdf_path) as pdf:
            
            for page_num in range(target_page, len(pdf.pages)):

                text = pdf.pages[page_num].extract_text()

                if not text:
                    continue

                lines = text.split("\n")

                for line in lines:

                    # 章节标题
                    if section_pattern.match(line):

                        if not found_start:
                            found_start = True
                        else:
                            return "\n".join(section_lines)

                    if found_start:
                        section_lines.append(line)

        return "\n".join(section_lines)

    # 提取命令-作用表格
    for subtitle, info in command_title_index.items():
        begin_page = info["begin_page"]
        commands = []

        page_num = begin_page

        while True:
            page_key = f"page_{page_num}"
            if page_key not in command_pdf_dict:
                break

            lines = command_pdf_dict[page_key]
            
            page_links = extract_command_links(command_reader, page_num - 1)
            height = command_pages[page_num-1].height

            # 🔑 唯一判定：是否为表格页
            if "命令 作用" not in lines:
                break

            header_idx = lines.index("命令 作用")

            # 只解析表头之后的内容
            for line in lines[header_idx + 1:]:
                # 跳过无关行
                if (
                    line.isdigit() or
                    roman_pattern.fullmatch(line) or
                    line.startswith("命令参考")
                ):
                    continue

                # 提取“命令 + 作用”
                m = desc_pattern.search(line)
                if not m:
                    continue

                description = m.group(1).strip()
                command = line[:m.start()].strip()

                if not command or not description:
                    continue

                link_dest = None

                for link in page_links:

                    x0, y0, x1, y1 = link["rect"]

                    height = command_pages[page_num-1].height

                    bbox = (x0, height - y1, x1, height - y0)

                    text = command_pages[page_num-1].within_bbox(bbox).extract_text()

                    if text and command in text:
                        link_dest = link["dest"]
                        break

                commands.append({
                    "subtitle": subtitle,
                    "command": command,
                    "description": description,
                    "dest": link_dest
                })
            # 继续下一页
            page_num += 1

        if commands:
            command_table[subtitle] = commands
            # print(commands)

    print("----------------------------------------------------------------")
    print("----------------------------------------------------------------")
    print("----------------------------------------------------------------")

    # 开始处理config_manual.txt
    with pdfplumber.open(config_pdf_path) as pdf:
        config_pages = pdf.pages
        total_pages = len(pdf.pages)

        in_toc_block = False
        toc_start_page = None

        for page_index in range(1, total_pages + 1):

            page = pdf.pages[page_index - 1]
            text = page.extract_text()

            if text:
                lines = [line.strip() for line in text.split("\n") if line.strip()]
            else:
                lines = []

            config_pdf_dict[f"page_{page_index}"] = lines

            if not lines:
                continue

            first_line = lines[0]
            print(f"检查第 {page_index} 页的第一行: {first_line}")

            # ✅ Step 1：识别目录起点
            if not in_toc_block and first_line.replace(" ", "") == "目录":
                in_toc_block = True
                toc_start_page = page_index
                continue

            # ✅ Step 2：在目录块中寻找“配置指南”
            if in_toc_block:

                match2 = re.match(r'^配置指南\s+(.+)$', first_line)

                if match2:
                    extracted_content = match2.group(1)

                    for substtles in config_category.values():
                        if extracted_content in substtles:

                            if extracted_content not in config_title_index:
                                config_title_index[extracted_content] = {
                                    "begin_page": toc_start_page
                                }
                            break

                    # 🔥🔥🔥 核心：命中后立刻退出目录块
                    in_toc_block = False
                    toc_start_page = None

                    continue

                # ❗否则继续留在目录块（因为是目录内容页）
                continue

    # 补全错误匹配的subtitle目录页码（根据实际文档内容人工补全）
    for subtitles in config_category.values(): 
        for subtitle in subtitles: 
            if subtitle in config_title_index: 
                print(f"{subtitle}: {config_title_index[subtitle]['begin_page']}") 
            else: 
                if subtitle == "Uboot 操作":
                    config_title_index[subtitle] = {'begin_page': 144}
                elif subtitle == "Rboot 操作":
                    config_title_index[subtitle] = {'begin_page': 151}
                elif subtitle == "Hungtask 命令":
                    config_title_index[subtitle] = {'begin_page': 196}
                elif subtitle == "TCAM 模式管理命令":
                    config_title_index[subtitle] = {'begin_page': 199}
                elif subtitle == "ECC 修复命令":
                    config_title_index[subtitle] = {'begin_page': 203}
                elif subtitle == "MAC 地址":
                    config_title_index[subtitle] = {'begin_page': 331}
                elif subtitle == "端口回环":
                    config_title_index[subtitle] = {'begin_page': 347}
                elif subtitle == "IPv4 基础":
                    config_title_index[subtitle] = {'begin_page': 729}
                elif subtitle == "DHCP 客户端":
                    config_title_index[subtitle] = {'begin_page': 785}
                elif subtitle == "IPv6 基础":
                    config_title_index[subtitle] = {'begin_page': 819}
                elif subtitle == "DHCPv6 客户端":
                    config_title_index[subtitle] = {'begin_page': 858}
                elif subtitle == "IP 快转":
                    config_title_index[subtitle] = {'begin_page': 915}
                elif subtitle == "IP 路由基础":
                    config_title_index[subtitle] = {'begin_page': 927}
                elif subtitle == "IPv4 组播路由管理":
                    config_title_index[subtitle] = {'begin_page': 1564}
                elif subtitle == "IPv6 组播路由管理":
                    config_title_index[subtitle] = {'begin_page': 1819}
                elif subtitle == "MPLS 基础":
                    config_title_index[subtitle] = {'begin_page': 2002}
                elif subtitle == "MPLS RAS(可靠性)":
                    config_title_index[subtitle] = {'begin_page': 2359}
                elif subtitle == "Segment Routing":
                    config_title_index[subtitle] = {'begin_page': 2407}
                elif subtitle == "队列缓存管理":
                    config_title_index[subtitle] = {'begin_page': 2651}
                elif subtitle == "CPP(CPU 保护策略)":
                    config_title_index[subtitle] = {'begin_page': 2775}
                elif subtitle == "uRPF(单播反向路径转发)":
                    config_title_index[subtitle] = {'begin_page': 2827}
                elif subtitle == "DoS 保护":
                    config_title_index[subtitle] = {'begin_page': 2837}
                elif subtitle == "FTP 服务器":
                    config_title_index[subtitle] = {'begin_page': 3114}
                elif subtitle == "FTP 客户端":
                    config_title_index[subtitle] = {'begin_page': 3123}
                elif subtitle == "TFTP 服务器":
                    config_title_index[subtitle] = {'begin_page': 3132}
                elif subtitle == "TFTP 客户端":
                    config_title_index[subtitle] = {'begin_page': 3138}
                elif subtitle == "VXLAN":
                    config_title_index[subtitle] = {'begin_page': 3274}
                else:
                    print(f"'{subtitle}': not found in the document")
                print(
                    f"'{subtitle}': starts at page {config_title_index[subtitle]['begin_page']}")

    # ================= 提取 config 目录（支持跨页 + 超链接） =================

    config_toc_table = {}

    for subtitle, info in config_title_index.items():

        begin_page = info["begin_page"]
        toc_items = []

        page_num = begin_page

        while True:

            page_key = f"page_{page_num}"
            if page_key not in config_pdf_dict:
                break

            lines = config_pdf_dict[page_key]

            # 🔥 关键：目录页特征（不是“配置指南”）
            if not lines:
                break

            first_line = lines[0]

            # ❗遇到“配置指南”说明目录结束
            if re.match(r'^配置指南\s+', first_line):
                break

            # 👉 提取该页链接
            page_links = extract_config_links(config_reader, page_num - 1)

            height = config_pages[page_num-1].height

            for line in lines:

                if line.replace(" ", "") == "目录":
                    continue
                # 跳过无效行
                if (
                    line.strip() == "" or
                    line.isdigit() or
                    re.match(r'^[ivxlcdm]+$', line, re.IGNORECASE)
                ):
                    continue

                link_dest = None

                for link in page_links:

                    x0, y0, x1, y1 = link["rect"]

                    height = config_pages[page_num-1].height
                    bbox = (x0, height - y1, x1, height - y0)

                    text = config_pages[page_num-1].within_bbox(bbox).extract_text()

                    if text and line[:10] in text:  # 粗匹配
                        link_dest = link["dest"]
                        break

                toc_items.append({
                    "subtitle": subtitle,
                    "title": line,
                    "dest": link_dest
                })

            page_num += 1

        if toc_items:
            config_toc_table[subtitle] = toc_items
            
    print(config_toc_table)

    print("\n========== CONFIG TOC ==========")

    config_toc_text = ""
    config_toc_index = {}   # {subtitle: {number: entry}}

    for subtitle, items in config_toc_table.items():
        subtitle_text, subtitle_index = build_config_toc_text_and_index(items)

        if not subtitle_text:
            continue

        config_toc_text += f"\n【{subtitle}】\n"
        config_toc_text += subtitle_text

        if subtitle not in config_toc_index:
            config_toc_index[subtitle] = {}
        for entry in subtitle_index:
            config_toc_index[subtitle][entry["number"]] = entry

    print(config_toc_text)
    print("\n========== CONFIG TOC END ==========")


    # print(command_title_index)
    # ================= 调试输出 =================
    # print("\n========== 命令表提取结果（严格表头判定） ==========")
    # for subtitle, cmds in command_table.items():
    #     print(f"\n【{subtitle}】 共 {len(cmds)} 条命令")
    #     for c in cmds:
    #         print(f"  {c['command']} -> {c['description']}")

    # ！！！！！！！！！！！！！！！！！！！输入的完整配置文件
    # configuration = """
    # router bgp 6
    #  bgp bestpath as-path multipath-relax
    #  bgp log-neighbor-changes
    #  bgp graceful-restart restart-time 120
    #  bgp graceful-restart stalepath-time 360
    #  bgp graceful-restart
    #  neighbor 192.168.2.65 remote-as 2000
    #  address-family ipv4
    #   maximum-paths ebgp 64
    #   network 10.51.6.0 mask 255.255.255.0
    #   neighbor 192.168.2.65 activate
    #   exit-address-family
    # """
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


    # =========================================================
    # Step: 使用 LLM 对 Ruijie 配置进行语义分片
    # =========================================================

    # 1 读取 prompt 模板
    with open(BASE_DIR / "divide_config_prompt_template.txt", "r", encoding="utf-8") as f:
        divide_template = f.read()

    # 2 准备填充变量
    src_device = "Ruijie"
    manuals = config_toc_text   # 如果以后要加入 manual，可以在这里填
    # suffix = ""

    # 3 构造 Prompt
    divide_prompt = (
        divide_template
        .replace("{src_device}", src_device)
        .replace("{manuals}", manuals)
        .replace("{configuration}", configuration)
    )

    print("\n========== CONFIG DIVIDE PROMPT ==========")
    print(divide_prompt)   # 防止打印太长


    # =========================================================
    # Step: 调用大模型
    # =========================================================

    fragments = []

    try:

        response = client.chat.completions.create(
            model="gpt-5.4",
            messages=[
                {
                    "role": "user",
                    "content": divide_prompt
                }
            ],
            temperature=0
        )

        divide_result = response.choices[0].message.content

        print("\n========== LLM RAW RESULT ==========")
        print(divide_result)

        # =====================================================
        # Step: 解析 JSON
        # =====================================================

        try:

            json_str = re.search(r"\[.*\]", divide_result, re.S).group()

            fragments = json.loads(json_str)
    
            print("\n========== PARSED FRAGMENTS ==========")
            print(fragments)

        except Exception as e:
            print("JSON 解析失败:", e)

    except Exception as e:
        print("LLM 调用失败:", e)


    # =========================================================
    # Step: 将 Fragment 重新拆回 configurations
    # =========================================================

    for index, frag in enumerate(fragments):
        fragment_text = frag.get("Fragment", "")

        ruijie_output.append({"ruijie_config":fragment_text, "target_config": "","command_manual":[], "config_manual":[]})

        fragment_configurations_list = [
            line.strip()
            for line in fragment_text.split("\n")
            if line.strip()
        ]
        frag["configurations_list"] = fragment_configurations_list

        subtitle_configurations = []# subtitle_configurations 是你已有的字符串列表，每行形如 "<subtitle>::<command>"
        results = []

        with open(BASE_DIR / "select_template.txt", "r", encoding="utf-8") as f:
            select_template = f.read()
            
        for cmd in fragment_configurations_list:
            cmd_wizout_p = re.sub(
                r'\b\d{1,3}(\.\d{1,3}){3}\b',  # 只匹配IPv4地址
                '',                             
                cmd
            )
            cmd_wizout_p = ' '.join(cmd_wizout_p.split())
            if cmd_wizout_p == "network mask":
                cmd_wizout_p = "network"
        #     # 构建prompt
        #     prompt = prompt_template.replace("{src_device}", src_device)

        #     prompt = prompt + f"""

        # ## CONFIGURATION
        # {configuration}

        # ## TARGET_COMMAND
        # {cmd}
        # """
        #         # 4 调用模型
        #         response = client.chat.completions.create(
        #             model="gpt-4o",
        #             messages=[
        #                 {
        #                     "role": "user",
        #                     "content": prompt
        #                 }
        #             ], stream=False
        #         )

        #         result = response.choices[0].message.content
        #         print(f"\n====== COMMAND ======")
        #         print(cmd)
        #         print("====== RESULT ======")
        #         print(result)
        #         results.append(result)
        #         print(type(result))
        #         # 解析 JSON 字符串
        #         json_str = re.search(r"\{.*\}", result, re.S).group()
        #         class_dict = json.loads(json_str)
        #         print(command_table[class_dict['Secondary_Section']])
            cmd_words = set(cmd_wizout_p.split())
            filtered_candidates = []
            for subtitle, commands in command_table.items():
                for command in commands:
                    cand_words = set(command["command"].split())
                    # 如果有单词重合则保留
                    if cmd_words & cand_words:
                        filtered_candidates.append(command)

            print(filtered_candidates)
            cmd_tokens = cmd_wizout_p.split()

            best_word_distance = float("inf")
            best_word_candidates = []

            # 第一阶段：单词级编辑距离
            for command in filtered_candidates:
                cand = command["command"]
                cand_tokens = cand.split()

                m = len(cmd_tokens)
                n = len(cand_tokens)

                dp = [[0]*(n+1) for _ in range(m+1)]

                for i in range(m+1):
                    dp[i][0] = i

                for j in range(n+1):
                    dp[0][j] = j

                for i in range(1, m+1):
                    for j in range(1, n+1):

                        if cmd_tokens[i-1] == cand_tokens[j-1]:
                            cost = 0
                        else:
                            cost = 1

                        dp[i][j] = min(
                            dp[i-1][j] + 1,
                            dp[i][j-1] + 1,
                            dp[i-1][j-1] + cost
                        )

                distance = dp[m][n]

                print(f"word distance: {cand} -> {distance}")

                if distance < best_word_distance:
                    best_word_distance = distance
                    best_word_candidates = [command]

                elif distance == best_word_distance:
                    best_word_candidates.append(command)

            print("\nWord distance best candidates:")
            print(best_word_candidates)


            # 第二阶段：字符级编辑距离
            best_char_distance = float("inf")
            best_matches = []

            for command in best_word_candidates:

                a = cmd_wizout_p
                cand = command["command"]
                b = cand

                m = len(a)
                n = len(b)

                dp = [[0]*(n+1) for _ in range(m+1)]

                for i in range(m+1):
                    dp[i][0] = i

                for j in range(n+1):
                    dp[0][j] = j

                for i in range(1, m+1):
                    for j in range(1, n+1):

                        if a[i-1] == b[j-1]:
                            cost = 0
                        else:
                            cost = 1

                        dp[i][j] = min(
                            dp[i-1][j] + 1,
                            dp[i][j-1] + 1,
                            dp[i-1][j-1] + cost
                        )

                char_distance = dp[m][n]

                print(f"char distance: {cand} -> {char_distance}")

                if char_distance < best_char_distance:
                    best_char_distance = char_distance
                    best_matches = [command]

                elif char_distance == best_char_distance:
                    best_matches.append(command)


            print("\n====== FINAL BEST MATCH ======")
            print(best_matches)
            print("char distance:", best_char_distance)
            print("best matches的长度:", len(best_matches))
            # 找到对应的命令信息
            target_clis = best_matches.copy()
            candidate_list = []

            for cli in target_clis:

                doc_text = extract_command_doc(cli["dest"])

                print("\n========== COMMAND ==========")
                print(cli["command"])

                print("\n========== SUBTITLE ==========")
                print(cli["subtitle"])

                print("\n========== COMMAND DOC ==========\n")
                print(doc_text)
            # ================= 构造 CANDIDATE_COMMANDS =================
                candidate_list.append({
                    "command": cli["command"],
                    "subtitle": cli["subtitle"],
                    "doc": doc_text  # ⚠️ 防止超长（很重要）doc_text[:1500]
                })
            selected_parsed = dict()
            if len(candidate_list) > 1:
                # 转 JSON 字符串
                candidate_json = json.dumps(candidate_list, ensure_ascii=False, indent=2)

                # ================= 构造 Prompt =================
                prompt = f"""
                {select_template}

                ## CONFIGURATION
                {configuration}

                ## TARGET_COMMAND
                {cmd}

                ## CANDIDATE_COMMANDS
                {candidate_json}
                """
                print("\n====== LLM PROMPT ======")
                print(prompt)
                print("\n====== LLM PROMPT END ======")
                # ================= 调用大模型 =================
                try:
                    # 4 调用模型
                    response = client.chat.completions.create(
                            model="gpt-5.4",
                            messages=[
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            temperature=0
                        )

                    result = response.choices[0].message.content

                    print("\n====== LLM RESULT ======")
                    print(result)

                    # ================= 解析 JSON =================
                    try:
                        json_str = re.search(r"\{.*\}", result, re.S).group()
                        selected_parsed = json.loads(json_str)

                        print("\n====== PARSED RESULT ======")
                        print(selected_parsed)
                        subtitle_configurations.append(f"{selected_parsed['Best_Subtitle']}::{cmd}")
                        print(subtitle_configurations)
                    except Exception as e:
                        print("JSON 解析失败:", e)

                except Exception as e:
                    print("LLM 调用失败:", e)

                """
                调用大语言模型 API 判断 TARGET_COMMAND 是否符合 COMMAND_TEMPLATE，并返回处理后的结果。
                :param target_command: 要评估的命令
                :param command_template: 模板命令
                :return: 处理后的 JSON 对象结果
                """
                # 读取 Prompt 模板
                with open(BASE_DIR / "confirm_template.txt", "r") as file:
                    confirm_template = file.read()

                for candidate in candidate_list:
                    if candidate["subtitle"] == selected_parsed["Best_Subtitle"]:
                        print("匹配成功")
                        
                        # 格式化 Prompt，将 TARGET_COMMAND 和 COMMAND_TEMPLATE 填充到模板中
                        filled_template = (
                            confirm_template
                                .replace("{DEVICE_NAME}", src_device)
                                + f"\n\nCOMMAND_TEMPLATE: {selected_parsed['Matched_Command_Template']}\nSUBTITLE: {selected_parsed['Best_Subtitle']}\nDoc from Manual: {candidate['doc']}\nTARGET_COMMAND: {cmd}\n"
                                # 如果模板中还有其它占位符，依次 replace
                        )
                        try:
                            response = client.chat.completions.create(
                                    model="gpt-5.4",
                                    messages=[
                                        {
                                            "role": "user",
                                            "content": filled_template
                                        }
                                    ],
                                    temperature=0
                                )

                            result = response.choices[0].message.content

                            print("\n====== LLM RESULT ======")
                            print(result)
                            # ================= 解析 JSON =================
                            try:
                                json_str = re.search(r"\{.*\}", result, re.S).group()
                                parsed = json.loads(json_str)

                                print("\n====== PARSED RESULT ======")
                                print(parsed)
                                if parsed["Match"] == "Yes":
                                    print("YesYesYesYesYesYesYesYesYesYesYesYesYesYes")
                                    ruijie_output[index]["command_manual"].append(candidate['doc'])
                                else:
                                    print("NoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNo")

                            except Exception as e:
                                print("JSON 解析失败:", e)
                        
                        except Exception as e:
                            print("LLM 调用失败:", e)
            else:
                """
                调用大语言模型 API 判断 TARGET_COMMAND 是否符合 COMMAND_TEMPLATE，并返回处理后的结果。
                :param target_command: 要评估的命令
                :param command_template: 模板命令
                :return: 处理后的 JSON 对象结果
                """
                # 读取 Prompt 模板
                with open(BASE_DIR / "confirm_template.txt", "r") as file:
                    confirm_template = file.read()

                # 格式化 Prompt，将 TARGET_COMMAND 和 COMMAND_TEMPLATE 填充到模板中
                filled_template = (
                    confirm_template
                        .replace("{DEVICE_NAME}", src_device)
                        + f"\n\nCOMMAND_TEMPLATE: {candidate_list[0]['command']}\nSUBTITLE: {candidate_list[0]['subtitle']}\nDoc from Manual: {candidate_list[0]['doc']}\nTARGET_COMMAND: {cmd}\n"
                        # 如果模板中还有其它占位符，依次 replace
                )
                try:
                    response = client.chat.completions.create(
                            model="gpt-5.4",
                            messages=[
                                {
                                    "role": "user",
                                    "content": filled_template
                                }
                            ],
                            temperature=0
                        )

                    result = response.choices[0].message.content

                    print("\n====== LLM RESULT ======")
                    print(result)
                    # ================= 解析 JSON =================
                    try:
                        json_str = re.search(r"\{.*\}", result, re.S).group()
                        parsed = json.loads(json_str)

                        print("\n====== PARSED RESULT ======")
                        print(parsed)
                        subtitle_configurations.append(f"{candidate_list[0]['subtitle']}::{cmd}")
                        print(subtitle_configurations)
                        if parsed["Match"] == "Yes":
                            print("YesYesYesYesYesYesYesYesYesYesYesYesYesYes")
                            ruijie_output[index]["command_manual"].append(candidate_list[0]['doc'])

                        else:
                            print("NoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNo")

                    except Exception as e:
                        print("JSON 解析失败:", e)
                
                except Exception as e:
                    print("LLM 调用失败:", e)


    # -----------------------------------------------------

        ##现在开始调用大模型对config manual的目录进行筛选
        # 0. 读取模板
        with open(BASE_DIR / "config_ml_select_template.txt", "r", encoding="utf-8") as f:
            config_ml_select_template = f.read()

        # 1. 准备要替换的内容
        device_name = src_device          # 根据实际设备名称赋值
        config_toc_text = config_toc_text # config manual 的目录全文
        target_config = "\n".join(subtitle_configurations) # configurations 是你已有的字符串列表，每行形如 "<subtitle>::<command>"
        ruijie_output[index]["target_config"] = target_config
        # 假设 prompt_template 里有 {DEVICE_NAME} 等占位符
        filled_template = (
            config_ml_select_template
                .replace("{DEVICE_NAME}", device_name)
                .replace("{CONFIG_TOC_TEXT}", config_toc_text)
                .replace("{TARGET_CONFIG}", target_config)
                # 如果模板中还有其它占位符，依次 replace
        )

        prompt = f"""
        {filled_template}
        """
        print("\n====== LLM PROMPT ======")
        print(prompt)
        print("\n====== LLM PROMPT END ======")

        # 3. 调用大模型
        try:
            response = client.chat.completions.create(
                model="gpt-5.4",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )
            result = response.choices[0].message.content

            print("\n====== LLM RAW RESULT ======")
            print(result)

            # 4. 解析 JSON（模板要求输出 JSON array）
            try:
                json_str = re.search(r"\[.*\]", result, re.S).group()
                parsed = json.loads(json_str)

                print("\n====== PARSED RESULT ======")
                print(parsed)

                # 5. 提取并打印目录编号（number 字段）和标题（subtitle 字段）
                pairs = [
                    (item.get("number"), item.get("subtitle"))
                    for item in parsed
                    if isinstance(item, dict)
                ]

                unique_pairs = list(dict.fromkeys(pairs))
                selected_unique_pairs= []

                print("\nMost relevant unique (number, subtitle) pairs:")
                for number, subtitle in unique_pairs:
                    print(f"number: {number}, subtitle: {subtitle}")


                # subtitles = [item.get("subtitle") for item in parsed if isinstance(item, dict)]
                # numbers = [item.get("number") for item in parsed if isinstance(item, dict)]
                # unique_numbers = list(set(numbers))#上面大模型返回的字章节可能重复，所以要去重
                # print("\nMost relevant unique section numbers:", unique_numbers)
                # print("\nCorresponding subtitles:", subtitles)

                for num, sub in unique_pairs:

                    found = False

                    for subtitle, num_dict in config_toc_index.items():
                        if sub == subtitle:
                            if num in num_dict:
                                entry = num_dict[num]

                                print("\n====== MATCHED SECTION ======")
                                print("Subtitle:", subtitle)
                                print("Number:", num)
                                print("Title:", entry["title"])
                                print("num_dict:", num_dict)
                                # 🔑 核心：提取正文
                                print("\n========== CONFIG DOC ==========")

                                doc_text = extract_config_doc(num, entry["dest"])

                                print("\n====== DOCUMENT CONTENT ======\n")
                                print(doc_text) 
                                
                                # 调用LLM对该config doc进行确认匹配
                                # 读取 Prompt 模板
                                with open(BASE_DIR / "confirm_config_template.txt", "r") as file:
                                    confirm_config_template = file.read()
                                
                                filled_template = (
                                            confirm_config_template
                                                .replace("{DEVICE_NAME}", src_device)
                                                + f"\n\nTARGET_FRAGMENT: {fragment_text}\nCANDIDATE_SECTION_SUBTITLE: {subtitle}\nCANDIDATE_SECTION_NAME: {entry['title']}\nCANDIDATE_SECTION_DOC: {doc_text}\n"
                                                # 如果模板中还有其它占位符，依次 replace
                                        )
                                try:
                                    response = client.chat.completions.create(
                                            model="gpt-5.4",
                                            messages=[
                                                {
                                                    "role": "user",
                                                    "content": filled_template
                                                }
                                            ],
                                            temperature=0
                                        )

                                    result = response.choices[0].message.content

                                    print("\n====== LLM RESULT ======")
                                    print(result)
                                    # ================= 解析 JSON =================
                                    try:
                                        json_str = re.search(r"\{.*\}", result, re.S).group()
                                        parsed = json.loads(json_str)

                                        print("\n====== PARSED RESULT ======")
                                        print(parsed)
                                        if parsed["Relevant"] == "Yes":
                                            print("YesYesYesYesYesYesYesYesYesYesYesYesYesYes")
                                            selected_unique_pairs.append((num, subtitle))
                                            ruijie_output[index]["config_manual"].append(doc_text)

                                        else:
                                            print("NoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNoNo")

                                    except Exception as e:
                                        print("JSON 解析失败:", e)
                                
                                except Exception as e:
                                    print("LLM 调用失败:", e)
                                            
                                found = True
                                break

                    if not found:
                        print(f"\n⚠️ 未找到编号 {num} 对应的目录")

                print("\nselected_unique_pairs (number, subtitle) pairs:")
                for number, subtitle in selected_unique_pairs:
                    print(f"number: {number}, subtitle: {subtitle}")

            except Exception as e:
                print("JSON 解析失败:", e)

        except Exception as e:
            print("LLM 调用失败:", e)
    print("ruijie_output:", ruijie_output)
    return ruijie_output