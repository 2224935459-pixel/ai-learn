# -*- coding: utf-8 -*-
"""
DeepSeek Agent 模板 (你自己的 key, 国内支付, 极便宜)
用法: 复制这个文件, 改 TOOLS / get_xxx 工具函数 / 下面 __main__ 里的提问, 就是新 Agent
关键点:
  - MODEL 用 deepseek-v4-flash (便宜, 支持 tool calls)
  - thinking 关掉 (否则 content 可能为空)
  - key 从 AITools/deepseek_key.txt 读, 不写死
"""
import json, urllib.request, urllib.error, os

HERE = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(HERE, "..", "deepseek_key.txt")   # AITools/deepseek_key.txt
BASE = "https://api.deepseek.com"
MODEL = "deepseek-v4-flash"

def get_key():
    return open(KEY_FILE, encoding="utf-8").read().strip()

# ===== 在这里定义你的工具 =====
# 工具1: 查价格 (示例, 删掉或换成你自己的)
PRICES = {"皮衣": 299, "连衣裙": 199, "牛仔裤": 159}
def get_price(cloth):
    return PRICES.get(cloth, "暂无该商品价格")
# 工具2: 查库存 (新加的)
STOCK = {"皮衣": 5, "连衣裙": 0, "牛仔裤": 12}
def get_stock(cloth):
    n = STOCK.get(cloth, 0)
    return f"库存{n}件" if n > 0 else "已售罄"

# 把工具告诉模型 (格式固定, OpenAI 兼容)
TOOLS = [
    {
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
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock",
            "description": "查询某件衣服的库存数量",
            "parameters": {
                "type": "object",
                "properties": {"cloth": {"type": "string", "description": "衣服名, 如 皮衣"}},
                "required": ["cloth"],
            },
        },
    },
]
def chat(user_msg):
    """发一条消息给 Agent, 返回完整响应 dict"""
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": user_msg}],
        "tools": TOOLS,
        "max_tokens": 300,
        "thinking": {"type": "disabled"},   # 关思考, 保证 content 有值
    }
    req = urllib.request.Request(
        BASE + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {get_key()}"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())

def run_tool(call):
    """根据模型想调的工具, 执行对应函数, 返回结果字符串"""
    fname = call["function"]["name"]
    args = json.loads(call["function"]["arguments"])
    if fname == "get_price":
        return str(get_price(args["cloth"]))
    if fname == "get_stock":
        return str(get_stock(args["cloth"]))
    return f"未知工具: {fname}"
if __name__ == "__main__":
    q = "皮衣还有货吗?"
    print("用户:", q)
    resp = chat(q)
    msg = resp["choices"][0]["message"]
    if msg.get("tool_calls"):
        call = msg["tool_calls"][0]
        print(f"AI 调工具: {call['function']['name']}({call['function']['arguments']})")
        print("工具返回:", run_tool(call))
    else:
        print("AI:", msg["content"])
