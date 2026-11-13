import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("LLM_API_KEY")
URL = "https://api.deepseek.com/v1/chat/completions"

def call_llm(prompt: str, temperature: float = 0.7):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }
    try:
        resp = requests.post(URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "❌ 请求超时：网络慢或者接口响应慢，请重试"
    except requests.exceptions.RequestException as e:
        return f"❌ 网络请求失败：{str(e)}"
    except KeyError:
        return "❌ API返回格式异常，检查密钥是否正确"


def build_prompt(house_info: str, style: str):
    # 19步：提示词模板，强制要求【标题+正文】，控制300字内
    prompt = f"""
你是上海租房小红书博主，写{style}风格租房笔记。
要求：
1. 输出严格分成两行：第一行=标题，第二行开始=正文
2. 正文带emoji，口语化，总字数控制在300字以内
3. 不要额外解释、不要前言后语
房源信息：
{house_info}
"""
    return prompt


def generate_three_version(house_info: str):
    """一次性生成三个风格文案"""
    style_list = ["温柔自住风", "性价比省钱风", "极简干净风"]
    res = {}
    for s in style_list:
        p = build_prompt(house_info, s)
        res[s] = call_llm(p)
    return res

def generate_tags(house_info: str):
    """根据房源生成8-12个小红书租房标签"""
    prompt = f"""
根据下面上海租房房源信息，输出8~12个小红书标签，格式#xxx，不要多余文字，不要解释。
房源：
{house_info}
"""
    tag_text = call_llm(prompt)
    return tag_text
