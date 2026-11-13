import streamlit as st
from llm_client import generate_three_version, call_llm, build_prompt, generate_tags
from checker import scan_text
from batch_helper import parse_line, process_one_house, export_to_excel
import pandas as pd

def render_form():
    st.subheader("📝 房源信息填写")
    community = st.text_input("小区名称/地段")
    house_type = st.selectbox("户型", ["1室1厅", "2室1厅", "3室1厅", "其他"])
    area = st.number_input("建筑面积（㎡）", min_value=0.0, step=0.1)
    rent = st.number_input("月租金（元）", min_value=0, step=100)
    subway = st.text_input("距离地铁")
    support = st.text_input("周边配套")
    floor = st.selectbox("楼层", ["低楼层", "中楼层", "高楼层"])
    decorate = st.selectbox("装修风格", ["简约原木", "奶油风", "极简冷白", "其他"])
    highlight = st.text_area("房源亮点")
    return {
        "community": community,
        "house_type": house_type,
        "area": area,
        "rent": rent,
        "subway": subway,
        "support": support,
        "floor": floor,
        "decorate": decorate,
        "highlight": highlight,
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

def split_title_content(raw_text: str):
    lines = raw_text.strip().splitlines()
    if len(lines) >= 2:
        title = lines[0]
        content = "\n".join(lines[1:])
    else:
        title = "暂无标题"
        content = raw_text
    return title, content

# ========== 页面主流程 ==========
st.title("长租公寓小红书AI内容助手")

with st.sidebar:
    st.header("设置区")
    st.selectbox("选择大模型", ["deepseek"])

tab_single, tab_batch = st.tabs(["🔹 单房源生成", "🔸 批量生成&导出Excel"])

# ========== 单房源（原有功能不变） ==========
with tab_single:
    form_data = render_form()
    submit_btn = st.button("✨ 一次性生成3版文案+标签")

    if "three_result" not in st.session_state:
        st.session_state["three_result"] = {}
    if "tags_result" not in st.session_state:
        st.session_state["tags_result"] = ""

    if submit_btn:
        if not form_data["community"] or form_data["rent"] <= 0:
            st.warning("小区名称和租金不能为空！")
        else:
            info = house_info_text(form_data)
            st.subheader("📋 你输入的房源信息")
            st.write(info)
            with st.spinner("正在生成3版文案+标签，请稍等..."):
                st.session_state["three_result"] = generate_three_version(info)
                st.session_state["tags_result"] = generate_tags(info)

    if st.session_state["three_result"]:
        info = house_info_text(form_data)
        t1, t2, t3 = st.tabs(["温柔自住风", "性价比省钱风", "极简干净风"])
        tabs_map = {"温柔自住风":t1, "性价比省钱风":t2, "极简干净风":t3}
        for style, tab in tabs_map.items():
            with tab:
                text = st.session_state["three_result"][style]
                title, content = split_title_content(text)
                st.markdown(f"### 📌 {title}")
                st.write(content)
                st.code(text, language="markdown")
                if st.button(f"🔄 重生成文案【{style}】", key=f"regen_text_{style}"):
                    prompt = build_prompt(info, style)
                    new_text = call_llm(prompt)
                    st.session_state["three_result"][style] = new_text
                    st.rerun()
                st.subheader("🔍 文案违禁词检查")
                hit, suggest = scan_text(text)
                if hit:
                    st.warning(f"⚠️ 命中风险词：{hit}")
                    for word, rep in suggest.items():
                        st.info(f"💡 【{word}】建议替换成：{rep}")
                else:
                    st.success("✅ 文案暂未检测到高危词")
        st.divider()
        st.subheader("🏷️ 自动生成话题标签")
        tag_str = st.session_state["tags_result"]
        st.write(tag_str)
        st.code(tag_str, language="markdown")
        st.subheader("🔍 标签违禁词检查")
        tag_hit, tag_suggest = scan_text(tag_str)
        if tag_hit:
            st.warning(f"⚠️ 标签命中风险词：{tag_hit}")
            for word, rep in tag_suggest.items():
                st.info(f"💡 【{word}】建议替换成：{rep}")
        else:
            st.success("✅ 标签暂未检测到高危词")

# ========== 批量生成板块（42~46） ==========
with tab_batch:
    st.subheader("批量房源输入")
    st.markdown("""
    两种方式任选其一：
    1. 粘贴多行，每行格式：`小区,户型,面积,租金,地铁,配套,楼层,装修,亮点`
    示例：`浦上湾,1室1厅,47,3200,8号线,万达,中楼层,简约原木,采光好`
    2. 上传Excel，表头必须和上面字段顺序一致
    """)
    text_input = st.text_area("多行房源粘贴区", height=180)
    upload_file = st.file_uploader("上传Excel批量房源", type=["xlsx"])

    batch_run = st.button("🚀 开始批量生成（会比较久，API要逐个调用）")
    if "batch_result" not in st.session_state:
        st.session_state["batch_result"] = []

    if batch_run:
        raw_list = []
        # 读取文本框
        if text_input.strip():
            lines = text_input.strip().splitlines()
            for line in lines:
                d = parse_line(line)
                if d:
                    raw_list.append(d)
                else:
                    st.warning(f"跳过格式错误行：{line}")
        # 读取上传Excel
        if upload_file is not None:
            df_upload = pd.read_excel(upload_file)
            for _, row in df_upload.iterrows():
                d = {
                    "community": str(row.iloc[0]),
                    "house_type": str(row.iloc[1]),
                    "area": str(row.iloc[2]),
                    "rent": str(row.iloc[3]),
                    "subway": str(row.iloc[4]),
                    "support": str(row.iloc[5]),
                    "floor": str(row.iloc[6]),
                    "decorate": str(row.iloc[7]),
                    "highlight": str(row.iloc[8]),
                }
                raw_list.append(d)
        if len(raw_list) == 0:
            st.error("没有读到有效房源！检查格式")
        else:
            st.info(f"一共 {len(raw_list)} 条房源，开始处理")
            progress = st.progress(0)
            out_list = []
            for idx, one in enumerate(raw_list):
                progress.progress((idx+1)/len(raw_list), text=f"正在处理：{one['community']}")
                res = process_one_house(one)
                out_list.append(res)
            st.session_state["batch_result"] = out_list
            st.success("✅ 批量全部生成完成！")

    # 展示表格 + 下载按钮
    if len(st.session_state["batch_result"]) > 0:
        st.subheader("📋 批量结果预览")
        df_out = pd.DataFrame(st.session_state["batch_result"])
        st.dataframe(df_out, height=300)
        excel_bytes = export_to_excel(st.session_state["batch_result"])
        st.download_button(
            label="📥 下载全部结果Excel",
            data=excel_bytes,
            file_name="房源小红书文案批量结果.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
