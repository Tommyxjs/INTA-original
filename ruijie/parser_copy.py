import pdfplumber
import re

pdf_path = "ruijie_command_manual.pdf"
output_txt = "ruijie_command_manual.txt"

# 用于存储最终结果的字典
pdf_dict = {}

title_index = {}  # 存储每个二级标题的起始页码

category = {
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


with pdfplumber.open(pdf_path) as pdf:
    for page_index, page in enumerate(pdf.pages, start=1):
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
            #     if extracted_content in category:
            #         category[extracted_content]["begin_page"] = page_index
            #         result_dict[current_key] = []  # 初始化key对应的value列表
            #     # print(f"在第 {page_index} 页找到第一种匹配项: {extracted_content}")
            # else:
            # 第二种情况：匹配 "命令参考 内容" 格式
            match2 = re.match(r'^命令参考\s+(.+)$', first_line)
            if match2:
                extracted_content = match2.group(1)
                found = False
                for substtles in category.values():
                    if extracted_content in substtles:
                        if extracted_content not in title_index:
                            title_index[extracted_content] = {
                                "begin_page": page_index}
                        found = True
                        break
                # print(f"在第 {page_index} 页找到第二种匹配项: {extracted_content}")

        pdf_dict[f"page_{page_index}"] = lines

# ========== 格式化写入 TXT ==========
with open(output_txt, "w", encoding="utf-8") as f:
    for page, lines in pdf_dict.items():
        f.write(f"{'=' * 12} {page.upper()} {'=' * 12}\n")
        for line in lines:
            f.write(line + "\n")
        f.write("\n")

print("✅ ruijie_command_manual.pdf 已成功转换为结构化文本")
# # 逐行打印每个key的内容、value长度和value内容
# for key, values in result_dict.items():
#     print(f"Key: {key}")
#     print(f"Value 长度: {len(values)}")
#     print(f"Value 内容: {values}")
#     print("-" * 40)  # 分隔线，便于阅读

# print("\ncategory 字典信息:")
# print("title_1 has ", len(category.keys()), " keys")
# for key, values in category.items():
#     print(f"Key: {key}")
#     print(f"Value 长度: {len(values)}")
#     print(f"Value 内容: {values}")
#     print("-" * 40)  # 分隔线，便于阅读
# print(title_index)
print("--------------------------------")
for subtitles in category.values():
    for subtitle in subtitles:
        if subtitle in title_index:
            print(
                f"'{subtitle}': starts at page {title_index[subtitle]['begin_page']}")
        else:
            if subtitle == "转发表模式管理":
                title_index[subtitle] = {'begin_page': 374}
            elif subtitle == "Hungtask 命令":
                title_index[subtitle] = {'begin_page': 449}
            elif subtitle == "TCAM 模式管理命令":
                title_index[subtitle] = {'begin_page': 456}
            elif subtitle == "ECC 修复命令":
                title_index[subtitle] = {'begin_page': 459}
            elif subtitle == "MAC 地址":
                title_index[subtitle] = {'begin_page': 694}
            elif subtitle == "端口回环":
                title_index[subtitle] = {'begin_page': 735}
            elif subtitle == "IPv4 基础":
                title_index[subtitle] = {'begin_page': 1078}
            elif subtitle == "DHCP 客户端":
                title_index[subtitle] = {'begin_page': 1214}
            elif subtitle == "IPv6 基础":
                title_index[subtitle] = {'begin_page': 1268}
            elif subtitle == "DHCPv6 客户端":
                title_index[subtitle] = {'begin_page': 1395}
            elif subtitle == "IP 快转":
                title_index[subtitle] = {'begin_page': 1437}
            elif subtitle == "IP 路由基础":
                title_index[subtitle] = {'begin_page': 1499}
            elif subtitle == "IPv4 组播路由管理":
                title_index[subtitle] = {'begin_page': 2587}
            elif subtitle == "IPv6 组播路由管理":
                title_index[subtitle] = {'begin_page': 2824}
            elif subtitle == "MPLS 基础":
                title_index[subtitle] = {'begin_page': 2965}
            elif subtitle == "MPLS RAS(可靠性)":
                title_index[subtitle] = {'begin_page': 3058}
            elif subtitle == "Segment Routing":
                title_index[subtitle] = {'begin_page': 3067}
            elif subtitle == "队列缓存管理":
                title_index[subtitle] = {'begin_page': 3378}
            elif subtitle == "CPP(CPU 保护策略)":
                title_index[subtitle] = {'begin_page': 3629}
            elif subtitle == "uRPF(单播反向路径转发)":
                title_index[subtitle] = {'begin_page': 3825}
            elif subtitle == "DoS 保护":
                title_index[subtitle] = {'begin_page': 3835}
            elif subtitle == "FTP 服务器":
                title_index[subtitle] = {'begin_page': 4199}
            elif subtitle == "FTP 客户端":
                title_index[subtitle] = {'begin_page': 4221}
            elif subtitle == "TFTP 服务器":
                title_index[subtitle] = {'begin_page': 4228}
            elif subtitle == "TFTP 客户端":
                title_index[subtitle] = {'begin_page': 4234}
            elif subtitle == "IFA":
                title_index[subtitle] = {'begin_page': 4444}
            elif subtitle == "PFC":
                title_index[subtitle] = {'begin_page': 4650}
            else:
                print(f"'{subtitle}': not found in the document")
            print(
                f"'{subtitle}': starts at page {title_index[subtitle]['begin_page']}")

# ================= 提取“命令-作用”表格（严格以表头为准，支持跨页） =================

command_table = {}

# 匹配末尾中文“作用描述”
desc_pattern = re.compile(r'([\u4e00-\u9fa5].*)$')

# 匹配整行罗马数字页脚（i / ii / iii / iv ...）
roman_pattern = re.compile(r'^[ivxlcdm]+$', re.IGNORECASE)

for subtitle, info in title_index.items():
    begin_page = info["begin_page"]
    commands = []

    page_num = begin_page

    while True:
        page_key = f"page_{page_num}"
        if page_key not in pdf_dict:
            break

        lines = pdf_dict[page_key]

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

            commands.append({
                "command": command,
                "description": description
            })

        # 继续下一页
        page_num += 1

    if commands:
        command_table[subtitle] = commands
        print(commands)

# print(title_index)
# ================= 调试输出 =================
# print("\n========== 命令表提取结果（严格表头判定） ==========")
# for subtitle, cmds in command_table.items():
#     print(f"\n【{subtitle}】 共 {len(cmds)} 条命令")
#     for c in cmds:
#         print(f"  {c['command']} -> {c['description']}")
