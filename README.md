\# 长租公寓小红书 AI 内容助手



面向长租公寓运营场景的 AI 文案生成工具：输入房源信息，自动产出多风格小红书笔记、话题标签，并做违禁词风险检测；支持批量生成并导出 Excel。



\## ✨ 已实现功能



\- \*\*单房源生成\*\*：填写房源信息后，一次生成 3 种风格文案

&#x20; - 温柔自住风 / 性价比省钱风 / 极简干净风

\- \*\*话题标签\*\*：根据房源自动生成 8～12 个小红书 #话题标签

\- \*\*违禁词检测\*\*：本地词库扫描文案与标签，命中风险词并给出中性替换建议

\- \*\*单版重生成\*\*：对不满意的某一版可单独重新生成，无需重填表单

\- \*\*一键复制\*\*：文案、标签均放入代码框，右上角可直接复制

\- \*\*批量处理\*\*：粘贴多行房源（逗号分隔）或上传 Excel，逐条生成

\- \*\*进度提示\*\*：批量生成时显示进度条

\- \*\*结果导出\*\*：批量结果预览成表，一键下载 `.xlsx`



\### 🚧 预留模块（待接入）



\- \*\*ComfyUI 本地配图\*\*：`app/comfy\_client.py` 已封装提交任务、轮询取图、保存到 `output/` 的逻辑，当前页面暂未接入；待本地 ComfyUI 环境就绪后，在页面中调用 `run\_comfy\_generate()` 即可。



\## 🛠️ 技术栈



\- Python 3.10～3.12

\- Streamlit（页面）

\- pandas + openpyxl（Excel 处理与导出）

\- requests（大模型 / ComfyUI 接口调用）

\- python-dotenv（读取环境变量）

\- DeepSeek 大模型 API（文案 / 标签生成）



\## 📁 目录结构



apartment-ai-assistant/

├── app/

│   ├── main.py            # Streamlit 主页面

│   ├── llm\_client.py      # 大模型调用、提示词模板、三版文案、标签生成

│   ├── checker.py         # 违禁词加载、扫描、替换建议

│   ├── batch\_helper.py    # 批量解析、逐条处理、导出 Excel

│   └── comfy\_client.py    # ComfyUI 客户端（预留）

├── data/

│   ├── sample.txt         # 测试样例房源

│   └── banned\_words.txt   # 违禁词词库（一行一个词，可自行增删）

├── output/                # 生成的图片 / 文件（不提交 Git）

├── docs/                  # 需求文档、字段说明、截图

├── .env                   # API Key（不提交 Git）

└── README.md



```



1. 🚀 安装与运行



\### 1. 创建并激活虚拟环境



Windows CMD：



```bash

python -m venv venv

venv\\Scripts\\activate

```
### 2. 安装依赖

```
pip install streamlit pandas openpyxl python-dotenv requests pillow
```

### 3. 配置 API Key

在项目根目录新建 `.env` 文件：

```
LLM_API_KEY=你的DeepSeek密钥
```

> 
> Key 只写在 `.env` 里，不要硬编码到代码中，也不要提交到 Git。

### 4. 启动页面

```
streamlit run app/main.py
```

浏览器打开终端提示的本地地址（默认 `http://localhost:8501`）。

## 📋 批量输入格式

每行一条房源，字段顺序为：

```
小区,户型,面积,租金,地铁,配套,楼层,装修,亮点
```

示例：

```
浦上湾,1室1厅,47,2916,8号线浦江镇,浦江万达,中楼层,简约原木,采光好独立厨卫
```

## 📌 说明

- 所有 AI 生成内容均为辅助草稿，发布前请人工核对事实与合规性。
- 违禁词库为基础版本，可根据平台规则持续在 `data/banned_words.txt` 中补充。