# -*- coding: utf-8 -*-
# 对比: 同一个写文案任务, DeepSeek V4 Flash vs OpenRouter ling:free
import json, urllib.request, urllib.error, os

HERE = os.path.dirname(os.path.abspath(__file__))
AITOOLS = os.path.abspath(os.path.join(HERE, ".."))   # AITools 根
KEYS = os.path.join(AITOOLS, "keys")

def deepseek_key():
    return open(os.path.join(KEYS, "deepseek_key.txt"), encoding="utf-8").read().strip()
def or_key():
    return open(os.path.join(KEYS, "openrouter_key.txt"), encoding="utf-8").read().strip()

def call(url, key, model, prompt, headers_extra=None, disable_think=False):
    body = {"model": model,
        "messages": [{"role":"user","content": prompt}],
        "max_tokens": 250}
    if disable_think:
        body["thinking"] = {"type": "disabled"}
    payload = json.dumps(body).encode()
    h = {"Content-Type":"application/json","Authorization":f"Bearer {key}"}
    if headers_extra: h.update(headers_extra)
    req = urllib.request.Request(url, data=payload, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return f"!! HTTP {e.code}: {e.read().decode('utf-8','ignore')[:150]}"

PROMPT = "写一条小红书文案推荐'米白色羊毛混纺半身裙, 高腰显瘦通勤', 带标题和标签, 30字内"

print("="*60)
print("任务:", PROMPT)
print("="*60)

print("\n【A】DeepSeek V4 Flash:")
print(call("https://api.deepseek.com/chat/completions", deepseek_key(),
           "deepseek-v4-flash", PROMPT, disable_think=True))

print("\n【B】OpenRouter ling:free:")
print(call("https://openrouter.ai/api/v1/chat/completions", or_key(),
           "inclusionai/ling-3.0-flash:free", PROMPT,
           {"HTTP-Referer":"http://localhost","X-Title":"cmp"}))
