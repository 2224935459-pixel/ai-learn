# -*- coding: utf-8 -*-
# 朴素 RAG 示例: 基于本地资料文件回答
import json, urllib.request, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))   # AITools 根
KEY_FILE = os.path.join(ROOT, "keys", "deepseek_key.txt")
KNOWLEDGE_FILE = os.path.join(ROOT, "data", "knowledge.txt")
BASE = "https://api.deepseek.com"
MODEL = "deepseek-v4-flash"

# ===== 资料加载: 从 knowledge.txt 读取 =====
def load_knowledge():
    kf = KNOWLEDGE_FILE
    with open(kf, encoding="utf-8") as f:
        return f.read()

KNOWLEDGE = load_knowledge()

def get_key():
    return open(KEY_FILE, encoding="utf-8").read().strip()

def ask(question):
    # 将资料与问题拼接, 约束模型仅基于资料作答
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
    q = "牛仔裤第一次洗要注意什么?"
    print("问:", q)
    print("-" * 40)
    print(ask(q))
