# -*- coding: utf-8 -*-
"""全自动「保人 换背景」脚本（你不用手涂蒙版）。
流程：原图 → ComfyUI 内置 BiRefNet 自动抠人(出蒙版) → 局部重绘换背景 → 存图。

你只要做两件事：
  1) 把照片(单人照最好)丢进 input_photos/ 文件夹（任意名字，如 xiaoming.png）
  2) 改下面 PROMPT 那行 = 你想要的背景描述
然后双击运行（或终端跑），结果在 output/。

注意：第一次跑会自动下载 BiRefNet 抠图模型(约几百MB,一次性)，要联网、稍慢。
注意：z-image-turbo 做换背景时背景是 AI 随机发挥，受提示词控制较弱；脸一定能保住。
"""
import json, time, os, glob, urllib.request, urllib.error, urllib.parse

COMFY = "http://127.0.0.1:8188"
BASE = "C:/Users/22249/Desktop/AITools/batch_bg"
IN_DIR = f"{BASE}/input_photos"
OUT_DIR = f"{BASE}/output"
CLIENT_ID = "hermes_batch"

# ===== 唯一要改的旋钮：背景描述 =====
PROMPT = "白色底片"

def upload_image(path, name):
    with open(path, "rb") as f:
        data = f.read()
    boundary = "----hermesboundary"
    head = (f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\n"
            f"Content-Type: image/png\r\n\r\n").encode()
    tail = (f"\r\n--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"type\"\r\n\r\ninput\r\n"
            f"--{boundary}--\r\n").encode()
    body = head + data + tail
    req = urllib.request.Request(f"{COMFY}/upload/image", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())

def build_workflow(img_name):
    # BiRefNet 抠图: 人=白(保留), 背景=黑(重绘)
    return {
        "1": {"class_type": "UNETLoader",
              "inputs": {"unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "lumina2"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
        "4": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["1", 0], "shift": 3}},
        "5": {"class_type": "LoadImage", "inputs": {"image": img_name}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": PROMPT}},
        "7": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["6", 0]}},
        # ---- 自动抠图 ----
        "20": {"class_type": "LoadBackgroundRemovalModel", "inputs": {"bg_removal_name": "birefnet.safetensors"}},
        "21": {"class_type": "RemoveBackground", "inputs": {"bg_removal_model": ["20", 0], "image": ["5", 0]}},
        # BiRefNet 出的蒙版: 人=白(前景). 但 VAEEncodeForInpaint 约定 白=重绘区, 所以反相
        "22": {"class_type": "InvertMask", "inputs": {"mask": ["21", 0]}},
        "8": {"class_type": "VAEEncodeForInpaint",
              "inputs": {"pixels": ["5", 0], "vae": ["3", 0], "mask": ["22", 0], "grow_mask_by": 0}},
        # ---- 重绘 ----
        "9": {"class_type": "KSampler",
              "inputs": {"model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0],
                         "latent_image": ["8", 0], "seed": int(time.time()) % 1000000,
                         "steps": 4, "cfg": 3.0, "sampler_name": "res_multistep",
                         "scheduler": "simple", "denoise": 0.6}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["9", 0], "vae": ["3", 0]}},
        "11": {"class_type": "SaveImage", "inputs": {"images": ["10", 0], "filename_prefix": "batch_bg"}},
    }

def post_prompt(wf):
    payload = json.dumps({"prompt": wf, "client_id": CLIENT_ID}).encode()
    req = urllib.request.Request(f"{COMFY}/prompt", data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())["prompt_id"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        print("  !! 400 错误正文:", body[:1500])
        return None

def wait_and_save(pid):
    deadline = time.time() + 600
    while time.time() < deadline:
        with urllib.request.urlopen(f"{COMFY}/history", timeout=30) as r:
            hist = json.loads(r.read())
        if pid in hist:
            h = hist[pid]
            if h.get("status", {}).get("status_str") != "success":
                print("  !! 出图失败:", h.get("status")); return
            for node_out in h.get("outputs", {}).values():
                for im in node_out.get("images", []):
                    url = f"{COMFY}/view?filename={urllib.parse.quote(im['filename'])}&subfolder={im.get('subfolder','')}&type={im.get('type','output')}"
                    with urllib.request.urlopen(url, timeout=60) as rr:
                        data = rr.read()
                    out_path = f"{OUT_DIR}/{im['filename']}"
                    with open(out_path, "wb") as f:
                        f.write(data)
                    print("    -> 存到", out_path)
            return
        time.sleep(2)

def process_one(photo):
    """换一张图的背景, 返回换好背景的输出路径(失败返回 None)."""
    name = os.path.splitext(os.path.basename(photo))[0]
    up = upload_image(photo, os.path.basename(photo))
    real_name = up["name"]
    pid = post_prompt(build_workflow(real_name))
    if not pid:
        print("  跳过(发任务失败):", name); return None
    deadline = time.time() + 600
    while time.time() < deadline:
        with urllib.request.urlopen(f"{COMFY}/history", timeout=30) as r:
            hist = json.loads(r.read())
        if pid in hist:
            h = hist[pid]
            if h.get("status", {}).get("status_str") != "success":
                print("  !! 出图失败:", h.get("status")); return None
            for node_out in h.get("outputs", {}).values():
                for im in node_out.get("images", []):
                    url = f"{COMFY}/view?filename={urllib.parse.quote(im['filename'])}&subfolder={im.get('subfolder','')}&type={im.get('type','output')}"
                    with urllib.request.urlopen(url, timeout=60) as rr:
                        data = rr.read()
                    out_path = f"{OUT_DIR}/{im['filename']}"
                    with open(out_path, "wb") as f:
                        f.write(data)
                    print("    -> 存到", out_path)
                    return out_path
            return None
        time.sleep(2)
    return None

if __name__ == "__main__":
    # 只处理 input_photos 里直接的图片(自动抠图,不需要蒙版文件)
    photos = sorted(glob.glob(f"{IN_DIR}/*.png")) + sorted(glob.glob(f"{IN_DIR}/*.jpg")) + sorted(glob.glob(f"{IN_DIR}/*.jpeg"))
    photos = [p for p in photos if not os.path.basename(p).endswith("_mask.png") and "_withmask" not in os.path.basename(p)]
    print(f"找到 {len(photos)} 张照片，开始自动抠图+换背景\n")
    for photo in photos:
        name = os.path.splitext(os.path.basename(photo))[0]
        print(f"处理: {name}")
        up = upload_image(photo, os.path.basename(photo))
        real_name = up["name"]
        print("  上传完成:", up)
        pid = post_prompt(build_workflow(real_name))
        if not pid:
            print("  跳过(发任务失败):", name); continue
        print("  任务ID:", pid, "等待出图(首次含下载模型,可能慢)...")
        wait_and_save(pid)
    print("\n全部完成。结果在", OUT_DIR)
    try:
        import sys
        if sys.stdin and sys.stdin.isatty():
            input("按任意键关闭...")
    except EOFError:
        pass
