# -*- coding: utf-8 -*-
# 真·向量库 RAG: 资料切块 -> embedding向量化 -> 存Chroma -> 提问时检索最相关块再答
import json, urllib.request, os

HERE = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(HERE, "deepseek_key.txt")
BASE = "https://api.deepseek.com"
MODEL = "deepseek-v4-flash"

# ---------- 第1步: 读资料并切块 ----------
def load_chunks():
    kf = os.path.join(HERE, "knowledge.txt")
    with open(kf, encoding="utf-8") as f:
        text = f.read()
    # 按空行/条目切小块, 每块是一句保养知识
    raw = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("【")]
    # 把【标题】拼回后面的条目, 让每块带上下文
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
    return chunks

CHUNKS = load_chunks()

# ---------- 第2步: 建向量库 (Chroma) ----------
import chromadb
from chromadb.utils import embedding_functions

# 用默认 embedding 模型(all-MiniLM-L6-v2), 首次会从网上下权重
ef = embedding_functions.DefaultEmbeddingFunction()
client = chromadb.Client()
# 每次重建集合, 避免重复添加
try:
    client.delete_collection("clothing")
except Exception:
    pass
col = client.create_collection("clothing")
col.add(
    documents=CHUNKS,
    ids=[f"c{i}" for i in range(len(CHUNKS))],
)

# ---------- 第3步: 提问时检索最相关的块 ----------
def retrieve(question, k=3):
    res = col.query(query_texts=[question], n_results=k)
    return res["documents"][0]   # 返回最相关的k块文本

# ---------- 第4步: 用检索到的块问 DeepSeek ----------
def get_key():
    return open(KEY_FILE, encoding="utf-8").read().strip()

def ask(question):
    hits = retrieve(question, k=3)
    context = "\n".join(f"- {h}" for h in hits)
    prompt = (
        "下面是检索到的相关资料, 请只基于这些资料回答, 没有就说'资料未提及':\n"
        f"---资料---\n{context}\n---资料结束---\n\n"
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
    import sys
    # 用法1: 命令行带问题  python vector_rag.py "你的问题"
    # 用法2: 双击bat, 黑框里直接打字问
    if len(sys.argv) > 1:
        q = sys.argv[1]
    else:
        try:
            q = input("你问: ")
        except EOFError:
            q = "皮衣沾水怎么处理?"   # 无输入时的默认
    print("问:", q)
    print("检索到的相关块:")
    for h in retrieve(q, 3):
        print("  -", h)
    print("-" * 40)
    print(ask(q))
