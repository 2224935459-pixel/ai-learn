# -*- coding: utf-8 -*-
"""用 OpenRouter 调大模型说话 (OpenAI 兼容格式).
key 从本地文件读, 不写死在代码里.
唯一旋钮: MODEL(换模型) / 下面 chat() 里的问句.
"""
import json, urllib.request, urllib.error, os

KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "keys", "openrouter_key.txt")
BASE = "https://openrouter.ai/api/v1"

# ===== 唯一要改的旋钮: 用哪个模型 =====
# 免费档举例(随时可能变, 去 openrouter.ai 看 Models 页):
#   "meta-llama/llama-3.2-3b-instruct:free"
#   "google/gemini-2.0-flash-exp:free"
#   "qwen/qwen2.5-7b-instruct:free"
MODEL = "inclusionai/ling-3.0-flash:free"

def get_key():
    with open(KEY_FILE, encoding="utf-8") as f:
        return f.read().strip()

def chat(prompt, max_tokens=300):
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
            "X-Title": "my-test",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            j = json.loads(r.read())
        return j["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return f"!! 出错 HTTP {e.code}: {e.read().decode('utf-8','ignore')[:300]}"

if __name__ == "__main__":
    ans = chat("用一句话介绍你自己是谁")
    print("模型回答:\n", ans)
