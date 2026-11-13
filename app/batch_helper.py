import pandas as pd
from llm_client import generate_three_version, generate_tags
from checker import scan_text

def parse_line(line: str):
    """
    单行解析：小区,户型,面积,租金,地铁,配套,楼层,装修,亮点
    示例：浦上湾,1室1厅,47,3200,8号线,万达,中楼层,简约原木,采光好
    """
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 9:
        return None
    return {
        "community": parts[0],
        "house_type": parts[1],
        "area": parts[2],
        "rent": parts[3],
        "subway": parts[4],
        "support": parts[5],
        "floor": parts[6],
        "decorate": parts[7],
        "highlight": parts[8],
    }

def house_info_text(data):
    return f"""
小区：{data['community']}
户型：{data['house_type']}
面积：{data['area']} ㎡
租金：{data['rent']} 元/月
地铁：{data['subway']}
配套：{data['support']}
楼层：{data['floor']}
装修：{data['decorate']}
亮点：{data['highlight']}
"""

def process_one_house(row_data):
    """处理单条房源，返回打包结果"""
    info = house_info_text(row_data)
    three_text = generate_three_version(info)
    tags = generate_tags(info)

    # 分别检测3版文案违禁词
    check_result = {}
    for style, txt in three_text.items():
        hit, suggest = scan_text(txt)
        check_result[style] = {"hit": hit, "suggest": suggest}
    tag_hit, tag_suggest = scan_text(tags)

    return {
        "房源小区": row_data["community"],
        "户型": row_data["house_type"],
        "面积": row_data["area"],
        "租金": row_data["rent"],
        "地铁": row_data["subway"],
        "配套": row_data["support"],
        "楼层": row_data["floor"],
        "装修": row_data["decorate"],
        "亮点": row_data["highlight"],
        "温柔自住风文案": three_text["温柔自住风"],
        "性价比省钱风文案": three_text["性价比省钱风"],
        "极简干净风文案": three_text["极简干净风"],
        "话题标签": tags,
        "温柔自住风违规词": check_result["温柔自住风"]["hit"],
        "性价比省钱风违规词": check_result["性价比省钱风"]["hit"],
        "极简干净风违规词": check_result["极简干净风"]["hit"],
        "标签违规词": tag_hit,
    }

def export_to_excel(result_list):
    df = pd.DataFrame(result_list)
    output_bytes = pd.ExcelWriter("tmp_export.xlsx", engine="openpyxl")
    df.to_excel(output_bytes, index=False, sheet_name="房源文案")
    output_bytes.close()
    with open("tmp_export.xlsx", "rb") as f:
        return f.read()
