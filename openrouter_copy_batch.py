# -*- coding: utf-8 -*-
"""批量文案生成器: 读 products.txt, 每行一个产品, 逐个调大模型写3条小红书文案, 存成 txt.
key 从 AITools/openrouter_key.txt 读. 模型走 OpenRouter 免费档.
用法: 双击 run_copy_batch.bat
"""
import json, os, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(HERE, "openrouter_key.txt")
PRODUCTS = os.path.join(HERE, "products.txt")
OUT = os.path.join(HERE, "copy_out")
BASE = "https://openrouter.ai/api/v1"
MODEL = "inclusionai/ling-3.0-flash:free"

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
            "X-Title": "copy-batch",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return f"!! 出错 HTTP {e.code}: {e.read().decode('utf-8','ignore')[:300]}"

def make_prompt(prod):
    return (
        f"你是一个小红书种草文案写手。产品是：{prod}\n"
        "请写3条不同的小红书风格文案，每条包含：\n"
        "1) 一个吸引人的标题（带emoji）\n"
        "2) 2-3句种草正文\n"
        "3) 3-5个相关话题标签\n"
        "用中文，语气真实像普通买家分享，不要硬广感。"
    )

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with open(PRODUCTS, encoding="utf-8") as f:
        items = [l.strip() for l in f if l.strip()]
    print(f"读到 {len(items)} 个产品, 开始生成...\n")
    for i, prod in enumerate(items, 1):
        print(f"[{i}/{len(items)}] {prod}")
        text = chat(make_prompt(prod))
        fn = os.path.join(OUT, f"{i:02d}_{prod[:12]}.txt")
        with open(fn, "w", encoding="utf-8") as w:
            w.write(f"产品: {prod}\n\n{text}\n")
        print(f"   -> 存到 {os.path.basename(fn)}")
    print("\n全部完成! 文案在 AITools/copy_out/ 文件夹")
    try:
        import sys
        if sys.stdin and sys.stdin.isatty():
            input("按任意键关闭...")
    except EOFError:
        pass
