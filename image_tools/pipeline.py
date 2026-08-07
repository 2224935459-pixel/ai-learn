# -*- coding: utf-8 -*-
"""一条龙: 换背景 + 写文案, 全自动不打字.
用法:
  1) 把照片丢进 batch_bg/input_photos/, 文件名格式: 产品名_描述.png
     例: 半身裙_米白轻奢通勤风.png
  2) 双击 run_pipeline.bat
结果: 每张图换好背景 + 配套文案, 存到 batch_bg/output/pkg_产品名/
"""
import os, sys, json, urllib.request, urllib.error, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))   # AITools 根
BATCH = os.path.join(ROOT, "image_tools", "batch_bg")
IN = os.path.join(BATCH, "input_photos")
OUT = os.path.join(BATCH, "output")
KEY_FILE = os.path.join(ROOT, "keys", "openrouter_key.txt")
BASE = "https://openrouter.ai/api/v1"
MODEL = "inclusionai/ling-3.0-flash:free"

# 复用换背景脚本的函数
sys.path.insert(0, BATCH)
from batch_bg_swap import process_one

def get_key():
    return open(KEY_FILE, encoding="utf-8").read().strip()

def chat(prompt, max_tokens=500):
    payload = json.dumps({"model": MODEL,
        "messages": [{"role":"user","content":prompt}],
        "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(BASE+"/chat/completions", data=payload,
        headers={"Content-Type":"application/json","Authorization":f"Bearer {get_key()}",
                 "HTTP-Referer":"http://localhost","X-Title":"pipeline"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return f"!! 出错 HTTP {e.code}: {e.read().decode('utf-8','ignore')[:200]}"

def make_prompt(desc):
    return (f"你是一个小红书种草文案写手。这件衣服的特点是：{desc}\n"
            "请写3条不同的小红书风格文案，每条包含：\n"
            "1) 一个吸引人的标题（带emoji）\n2) 2-3句种草正文\n3) 3-5个话题标签\n"
            "用中文，语气真实像普通买家分享，不要硬广感。")

if __name__ == "__main__":
    import glob
    imgs = sorted(glob.glob(f"{IN}/*.png")) + sorted(glob.glob(f"{IN}/*.jpg")) + sorted(glob.glob(f"{IN}/*.jpeg"))
    imgs = [p for p in imgs if not os.path.basename(p).endswith("_mask.png") and "_withmask" not in os.path.basename(p)]
    if not imgs:
        print("input_photos 里没有图, 先丢一张(文件名: 产品名_描述.png)")
        input("按任意键关闭..."); raise SystemExit
    print(f"找到 {len(imgs)} 张图, 开始一条龙(换背景+写文案)...\n")
    for photo in imgs:
        stem = os.path.splitext(os.path.basename(photo))[0]
        prod, desc = (stem.split("_", 1) + [""])[:2] if "_" in stem else (stem, stem)
        print(f"[{prod}] 描述: {desc}")
        bg = process_one(photo)          # 换背景
        if not bg:
            print("  !! 换背景失败, 跳过"); continue
        text = chat(make_prompt(desc))   # 写文案
        pkg = os.path.join(OUT, f"pkg_{prod}")
        os.makedirs(pkg, exist_ok=True)
        shutil.copy(bg, os.path.join(pkg, os.path.basename(bg)))  # 图进套餐
        with open(os.path.join(pkg, "文案.txt"), "w", encoding="utf-8") as w:
            w.write(f"产品: {prod}\n描述: {desc}\n\n{text}\n")
        print(f"   -> 套餐: output/pkg_{prod}/ (图 + 文案.txt)\n")
    print("全部完成! 套餐在 batch_bg/output/pkg_*/")
    try:
        import sys
        if sys.stdin and sys.stdin.isatty():
            input("按任意键关闭...")
    except EOFError:
        pass
