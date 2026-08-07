# -*- coding: utf-8 -*-
"""用 Python 脚本调用 ComfyUI 的 API 自动出图（文生图）。
这是你「接 API / 写脚本」第一关：不用在界面点，脚本自动把任务发给 ComfyUI，
等它跑完，把图存到桌面。

唯一要改的「旋钮」就是下面这个 PROMPT —— 换成任何中文描述就能出不同图。
"""
import json, time, urllib.request, urllib.error, os

COMFY = "http://127.0.0.1:8188"
CLIENT_ID = "hermes_desktop_script"
OUT_DIR = "C:/Users/22249/Desktop"

# ===== 唯一要改的旋钮 =====
PROMPT = "赛博朋克城市夜景, 霓虹灯, 雨"
WIDTH, HEIGHT = 1024, 1024

def build_prompt(prompt, w, h):
    """拼出 ComfyUI API 需要的 workflow（节点图）。
    结构 = 你那个 z-image-turbo 模板的文生图版：
    UNET -> ModelSampling -> KSampler
    CLIP -> 文字编码 -> KSampler
    空Latent -> KSampler -> VAE解码 -> 保存图像
    """
    return {
        "1": {"class_type": "UNETLoader",
              "inputs": {"unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "lumina2"}},
        "3": {"class_type": "VAELoader",
              "inputs": {"vae_name": "ae.safetensors"}},
        "4": {"class_type": "ModelSamplingAuraFlow",
              "inputs": {"model": ["1", 0], "shift": 3}},
        "5": {"class_type": "CLIPTextEncode",
              "inputs": {"clip": ["2", 0], "text": prompt}},
        "6": {"class_type": "ConditioningZeroOut",
              "inputs": {"conditioning": ["5", 0]}},
        "7": {"class_type": "EmptySD3LatentImage",
              "inputs": {"width": w, "height": h, "batch_size": 1}},
        "8": {"class_type": "KSampler",
              "inputs": {"model": ["4", 0], "positive": ["5", 0], "negative": ["6", 0],
                         "latent_image": ["7", 0], "seed": int(time.time()) % 1000000,
                         "steps": 4, "cfg": 1.0, "sampler_name": "res_multistep",
                         "scheduler": "simple", "denoise": 1.0}},
        "9": {"class_type": "VAEDecode",
              "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveImage",
               "inputs": {"images": ["9", 0], "filename_prefix": "api_txt2img"}},
    }

def post_prompt(workflow):
    payload = json.dumps({"prompt": workflow, "client_id": CLIENT_ID}).encode()
    req = urllib.request.Request(COMFY + "/prompt",
                                 data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())["prompt_id"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        print("=== /prompt 返回 400 错误正文 ===")
        print(body[:2000])
        raise

def get_history(prompt_id, timeout=300):
    deadline = time.time() + timeout
    while time.time() < deadline:
        with urllib.request.urlopen(COMFY + "/history", timeout=30) as r:
            hist = json.loads(r.read())
        if prompt_id in hist:
            return hist[prompt_id]
        time.sleep(2)
    raise TimeoutError("等 ComfyUI 出图超时")

def save_first_image(history):
    """从 history 里取出生成的图，存到桌面。"""
    outs = history.get("outputs", {})
    for node_id, node_out in outs.items():
        for img in node_out.get("images", []):
            url = f"{COMFY}/view?filename={img['filename']}&subfolder={img.get('subfolder','')}&type={img.get('type','output')}"
            with urllib.request.urlopen(url, timeout=60) as r:
                data = r.read()
            path = os.path.join(OUT_DIR, "api_txt2img_" + str(int(time.time())) + ".png")
            with open(path, "wb") as f:
                f.write(data)
            return path
    raise RuntimeError("history 里没找到生成的图")

if __name__ == "__main__":
    print("① 发送任务给 ComfyUI ...")
    pid = post_prompt(build_prompt(PROMPT, WIDTH, HEIGHT))
    print("   任务ID:", pid)
    print("② 等待出图（ComfyUI 在后台跑，脚本轮询）...")
    hist = get_history(pid)
    if hist.get("status", {}).get("status_str") != "success":
        print("   出图失败：", hist.get("status"))
        raise SystemExit(1)
    path = save_first_image(hist)
    print("③ 完成！图已存到:", path)
