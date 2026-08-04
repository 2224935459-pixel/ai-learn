# -*- coding: utf-8 -*-
# Agent 用 DeepSeek V4 Flash (你自己的 key, 国内支付, 极便宜)
import json, urllib.request, urllib.error, os

HERE = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(HERE, "..", "deepseek_key.txt")   # 在上一级 AITools/ 下
BASE = "https://api.deepseek.com"          # DeepSeek 官方端点 (OpenAI 兼容)
MODEL = "deepseek-v4-flash"                # 便宜够用, 支持 tool calls

def get_key():
    return open(KEY_FILE, encoding="utf-8").read().strip()

PRICES = {"皮衣": 299, "连衣裙": 199, "牛仔裤": 159}
def get_price(cloth):
    return PRICES.get(cloth, "暂无该商品价格")

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
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {get_key()}"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())

if __name__ == "__main__":
    q = "皮衣多少钱?"
    print("用户问:", q)
    resp = chat_with_tools(q)
    msg = resp["choices"][0]["message"]
    if "tool_calls" in msg and msg["tool_calls"]:
        call = msg["tool_calls"][0]
        fname = call["function"]["name"]
        args = json.loads(call["function"]["arguments"])
        print(f"AI 决定调用工具: {fname}({args})")
        if fname == "get_price":
            print(f"工具返回: {get_price(args['cloth'])}")
    else:
        print("AI 直接回答:", msg["content"])
