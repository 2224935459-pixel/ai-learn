# -*- coding: utf-8 -*-
# Agent + RAG 合体: AI 既会调业务工具(价格/库存), 又会检索知识库(RAG)回答
import json, urllib.request, os

HERE = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(HERE, "deepseek_key.txt")
BASE = "https://api.deepseek.com"
MODEL = "deepseek-v4-flash"

PRICES = {"皮衣": 299, "连衣裙": 199, "牛仔裤": 159}
STOCK = {"皮衣": 5, "连衣裙": 0, "牛仔裤": 12}

def get_price(cloth):
    return f"{cloth}价格{PRICES.get(cloth, '未知')}元"

def get_stock(cloth):
    n = STOCK.get(cloth, 0)
    return f"库存{n}件" if n > 0 else "已售罄"

# ===== RAG: 建知识库 =====
import chromadb
from chromadb.utils import embedding_functions

ef = embedding_functions.DefaultEmbeddingFunction()
client = chromadb.Client()
try:
    client.delete_collection("agent_kb")
except Exception:
    pass
col = client.create_collection("agent_kb")
with open(os.path.join(HERE, "knowledge.txt"), encoding="utf-8") as f:
    text = f.read()
chunks = []
title = ""
for l in text.splitlines():
    l = l.strip()
    if not l:
        continue
    if l.startswith("【") and l.endswith("】"):
        title = l
        continue
    chunks.append(f"{title} {l}")
col.add(documents=chunks, ids=[f"k{i}" for i in range(len(chunks))])

def get_knowledge(question):
    hits = col.query(query_texts=[question], n_results=3)["documents"][0]
    return "\n".join(hits)

# ===== 工具清单 =====
TOOLS = [
    {"type": "function", "function": {
        "name": "get_price",
        "description": "查询某件衣服的价格",
        "parameters": {"type": "object",
                       "properties": {"cloth": {"type": "string", "description": "衣服名, 如 皮衣"}},
                       "required": ["cloth"]}}},
    {"type": "function", "function": {
        "name": "get_stock",
        "description": "查询某件衣服的库存数量",
        "parameters": {"type": "object",
                       "properties": {"cloth": {"type": "string", "description": "衣服名, 如 皮衣"}},
                       "required": ["cloth"]}}},
    {"type": "function", "function": {
        "name": "get_knowledge",
        "description": "从服装保养/游戏知识库检索相关资料来回答问题",
        "parameters": {"type": "object",
                       "properties": {"question": {"type": "string", "description": "要检索的问题"}},
                       "required": ["question"]}}},
]

def get_key():
    return open(KEY_FILE, encoding="utf-8").read().strip()

def chat(user_q):
    messages = [{"role": "user", "content": user_q}]
    for _ in range(5):   # 多轮: 有tool_calls就继续循环
        body = {"model": MODEL, "messages": messages, "tools": TOOLS,
                "max_tokens": 400, "thinking": {"type": "disabled"}}
        req = urllib.request.Request(BASE + "/chat/completions",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {get_key()}"})
        with urllib.request.urlopen(req, timeout=90) as r:
            resp = json.loads(r.read())
        msg = resp["choices"][0]["message"]
        messages.append(msg)
        if not msg.get("tool_calls"):
            return msg["content"]
        for tc in msg["tool_calls"]:
            fname = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"])
            if fname == "get_price":
                res = get_price(args["cloth"])
            elif fname == "get_stock":
                res = get_stock(args["cloth"])
            elif fname == "get_knowledge":
                res = get_knowledge(args["question"])
            else:
                res = f"未知工具: {fname}"
            print(f"  AI 调工具: {fname}({args}) -> {res}")
            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": res})
    return "(超过最大轮数)"

if __name__ == "__main__":
    q = "皮衣怎么保养? 另外皮衣多少钱, 还有货吗?"
    print("问:", q)
    print("-" * 40)
    print(chat(q))
