# -*- coding: utf-8 -*-
# 实测: 视觉模型(gemma-4)能不能读图并返回描述
import json, base64, urllib.request, urllib.error, os

KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "keys", "openrouter_key.txt")
BASE = "https://openrouter.ai/api/v1"
VISION = "google/gemma-4-26b-a4b-it:free"

# 用你换背景出的图做测试
IMG = r"C:/Users/22249/Desktop/AITools/batch_bg/output/batch_bg_00020_.png"

def get_key():
    return open(KEY_FILE, encoding="utf-8").read().strip()

def describe(img_path):
    b64 = base64.b64encode(open(img_path, "rb").read()).decode()
    data_url = f"data:image/png;base64,{b64}"
    payload = json.dumps({
        "model": VISION,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "用一句中文描述这张图片: 主体穿什么衣服、什么风格、背景是什么。"},
                {"type": "image_url", "url": data_url},
            ],
        }],
        "max_tokens": 200,
    }).encode()
    req = urllib.request.Request(
        BASE + "/chat/completions", data=payload,
        headers={"Content-Type":"application/json","Authorization":f"Bearer {get_key()}",
                 "HTTP-Referer":"http://localhost","X-Title":"vision-test"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return f"!! HTTP {e.code}: {e.read().decode('utf-8','ignore')[:300]}"

if __name__ == "__main__":
    import os
    if not os.path.exists(IMG):
        print("测试图不存在:", IMG)
    else:
        print("视觉模型返回:\n", describe(IMG))
