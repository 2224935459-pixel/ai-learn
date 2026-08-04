# -*- coding: utf-8 -*-
# 最小 Agent: 给 AI 一个工具, 让它自己决定调不调
import json, urllib.request, urllib.error

KEY_FILE = r"C:/Users/22249/Desktop/AITools/openrouter_key.txt"
BASE = "https://openrouter.ai/api/v1"
MODEL = "inclusionai/ling-3.0-flash:free"

def get_key():
    return open(KEY_FILE, encoding="utf-8").read().strip()

# === 工具1: 查价格 (AI 可以调用它) ===
PRICES = {"皮衣": 299, "连衣裙": 199, "牛仔裤": 159}
def get_price(cloth):
    return PRICES.get(cloth, "暂无该商品价格")

# 把工具告诉模型(格式固定)
TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_price",
        "description": "查询某件衣服的价格",
        "parameters": {
            "type": "object",
            "properties": {"cloth": {"type": "string", "description": "衣服名, 如 皮衣"}},
            "required": ["cloth"],
        },
    },
}]

def chat_with_tools(user_msg):
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": user_msg}],
        "tools": TOOLS,
        "max_tokens": 300,
    }).encode()
    req = urllib.request.Request(BASE + "/chat/completions", data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {get_key()}",
                 "HTTP-Referer": "http://localhost", "X-Title": "agent"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())

if __name__ == "__main__":
    q = "连衣裙多少钱?"
    print("用户问:", q)
    resp = chat_with_tools(q)
    msg = resp["choices"][0]["message"]
    # 看 AI 有没有"想调工具"
    if "tool_calls" in msg and msg["tool_calls"]:
        call = msg["tool_calls"][0]
        fname = call["function"]["name"]
        args = json.loads(call["function"]["arguments"])
        print(f"AI 决定调用工具: {fname}({args})")
        if fname == "get_price":
            result = get_price(args["cloth"])
            print(f"工具返回: {result}")
    else:
        print("AI 直接回答:", msg["content"])
