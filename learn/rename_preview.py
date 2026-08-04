# 批量重命名练习(安全版: 只显示会改成啥, 不真改)
# 学: for 循环 + 字符串格式化 {i:02d} (编号补零) + 文件路径操作
import os

FOLDER = r"C:/Users/22249/Desktop/AITools/batch_bg/input_photos"

files = [f for f in os.listdir(FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
# 按文件名排序, 保证顺序稳定
files.sort()

print(f"文件夹里有 {len(files)} 张图, 重命名预览:")
for i, name in enumerate(files, 1):
    ext = os.path.splitext(name)[1]          # 取出 .png / .jpg
    new_name = f"商品{i:02d}{ext}"           # 商品01.png / 商品02.jpg
    print(f"  {name}  ->  {new_name}")
