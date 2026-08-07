# -*- coding: utf-8 -*-
# 社媒文案工具: 给平台+话题, 用 DeepSeek 写符合风格的文案
# 旋钮: 改下面 PLATFORM 和 TOPIC 就行
import json, urllib.request, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))   # AITools 根
KEY_FILE = os.path.join(ROOT, "keys", "deepseek_key.txt")   # AITools/keys/deepseek_key.txt
BASE = "https://api.deepseek.com"
MODEL = "deepseek-v4-flash"

# ===== 旋钮 =====
PLATFORM = "朋友圈"          # 改 "微博" 试试
TOPIC = "今天天气真好，出去逛了街"   # 改你要发的内容

def get_key():
    return open(KEY_FILE, encoding="utf-8").read().strip()

STYLE = {
    "朋友圈": "写一条微信朋友圈文案, 给年轻人看的丧系/emo风格。要求: 简短、丧但有态度、不装开心、可自嘲可阴阳怪气、带点虚无感、可加1-2个emoji、不要#话题标签#、不超过40字。示例味道: '又浪费了一天，挺好的。' '活着也就那样，凑合过。'",
    "微博": "写一条微博文案, 年轻人丧系/emo风格。要求: 可稍长、阴阳怪气带自嘲、有互动感、加1-2个#话题标签#、可加emoji、不超过80字。示例味道: '周末又要没了，我的快乐像工资一样薄。#废话文学#'",
}

def write_copy(platform, topic):
    prompt = f"{STYLE.get(platform, '写一条社交文案。')}\n内容主题: {topic}"
    body = {"model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200,
            "thinking": {"type": "disabled"}}
    req = urllib.request.Request(BASE + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {get_key()}"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]

if __name__ == "__main__":
    print(f"平台: {PLATFORM} | 主题: {TOPIC}")
    print("-" * 40)
    print(write_copy(PLATFORM, TOPIC))
