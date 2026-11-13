import os

# 词和推荐替换方案
REPLACE_MAP = {
    "最好": "很合适",
    "最低价": "价格友好",
    "绝对": "比较",
    "必看": "值得看看",
    "首选": "很适合",
    "秒杀": "性价比不错",
    "最便宜": "价格亲民",
    "无中介": "房东直签（谨慎）",
    "直租": "房源直签",
    "捡漏": "难得好房",
    "稳赚": "适合自住",
    "顶级": "品质不错",
    "第一": "靠前",
    "完美": "很舒服",
    "全网最低": "价格不错",
    "包过": "可沟通",
    "无敌": "体验很好",
    "黄金": "便利",
    "最强": "很不错"
}

def load_banned_words():
    """从txt加载违禁词列表"""
    txt_path = os.path.join("data", "banned_words.txt")
    if not os.path.exists(txt_path):
        return []
    with open(txt_path, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]
    return words

def scan_text(text: str):
    """扫描文本，返回命中词 + 替换建议"""
    banned = load_banned_words()
    hit_words = [w for w in banned if w in text]
    suggest = {}
    for w in hit_words:
        if w in REPLACE_MAP:
            suggest[w] = REPLACE_MAP[w]
        else:
            suggest[w] = "建议删除或改写"
    return hit_words, suggest
