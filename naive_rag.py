# -*- coding: utf-8 -*-
# 朴素 RAG: 把资料塞给 DeepSeek, 让它只基于资料回答 (不瞎编)
import json, urllib.request, os

HERE = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(HERE, "deepseek_key.txt")   # AITools/deepseek_key.txt
BASE = "https://api.deepseek.com"
MODEL = "deepseek-v4-flash"

# ===== 你的资料: 从 knowledge.txt 读 (改资料只改文件, 不动代码) =====
def load_knowledge():
    kf = os.path.join(HERE, "knowledge.txt")
    with open(kf, encoding="utf-8") as f:
        return f.read()

KNOWLEDGE = load_knowledge()

def get_key():
    return open(KEY_FILE, encoding="utf-8").read().strip()

def ask(question):
    # 关键: 把资料 + 问题拼一起, 并明确要求"只基于资料答"
    prompt = (
        "下面是参考资料, 请只根据参考资料回答, 资料里没有就说'资料未提及':\n"
        f"---资料---\n{KNOWLEDGE}\n---资料结束---\n\n"
        f"问题: {question}"
    )
    body = {"model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300,
            "thinking": {"type": "disabled"}}
    req = urllib.request.Request(BASE + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {get_key()}"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]

if __name__ == "__main__":
    q = "江少怎么保养"
    print("问:", q)
    print("-" * 40)
    print(ask(q))
