# -*- coding: utf-8 -*-
"""最小测试: 用脚本调 Nous Portal 让大模型说话 (OpenAI 兼容格式).
从 hermes 的 auth.json 读 key, 不硬编码、不打印.
"""
import json, urllib.request, os

AUTH = r"C:/Users/22249/AppData/Local/hermes/auth.json"

def get_cred():
    d = json.load(open(AUTH, encoding="utf-8", errors="ignore"))
    pool = d.get("credential_pool", {}).get("nous", [])
    if not pool:
        raise SystemExit("没找到 nous credential")
    c = pool[0]
    return c["inference_base_url"], c["access_token"]  # access_token 是秘钥, 仅内存使用

def chat(prompt):
    base, key = get_cred()
    payload = json.dumps({
        "model": "tencent/hy3:free",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
    }).encode()
    req = urllib.request.Request(
        base + "/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        j = json.loads(r.read())
    return j["choices"][0]["message"]["content"]

if __name__ == "__main__":
    out = chat("用一句话介绍你自己是谁")
    print("模型回答:", out)
