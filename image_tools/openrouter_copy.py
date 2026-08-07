# -*- coding: utf-8 -*-
"""服装文案生成器: 运行时让你输入产品描述, 调大模型写3条小红书文案.
key 从 openrouter_key.txt 读, 模型走 OpenRouter 免费档.
用法: 双击 run_copy.bat, 黑框里输入产品描述回车即可.
"""
import json, urllib.request, urllib.error, os

KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "keys", "openrouter_key.txt")
BASE = "https://openrouter.ai/api/v1"
MODEL = "inclusionai/ling-3.0-flash:free"

# 默认示例(运行时直接回车就用它)
DEFAULT_PRODUCT = "一条米白色羊毛混纺半身裙, 高腰显瘦, 秋冬通勤百搭"

def get_key():
    with open(KEY_FILE, encoding="utf-8") as f:
        return f.read().strip()

def chat(prompt, max_tokens=500):
    key = get_key()
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(
        BASE + "/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "copy-gen",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return f"!! 出错 HTTP {e.code}: {e.read().decode('utf-8','ignore')[:300]}"

if __name__ == "__main__":
    print("=" * 50)
    prod = input("输入产品描述(直接回车用示例): ").strip()
    if not prod:
        prod = DEFAULT_PRODUCT
    prompt = (
        f"你是一个小红书种草文案写手。产品是：{prod}\n"
        "请写3条不同的小红书风格文案，每条包含：\n"
        "1) 一个吸引人的标题（带emoji）\n"
        "2) 2-3句种草正文\n"
        "3) 3-5个相关话题标签\n"
        "用中文，语气真实像普通买家分享，不要硬广感。"
    )
    print("产品:", prod)
    print("=" * 50)
    print(chat(prompt))
    print("\n按任意键关闭...")
    input()
