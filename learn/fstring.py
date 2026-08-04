# f-string: 在字符串里用 {变量名} 自动填值
# 写法: 引号前面加 f, 里面用 {盒子名}

name = "小明"
clothes = "碎花连衣裙"
price = 199

# 普通拼法(麻烦): 用 + 把文字和变量连起来
print("店员:" + name + " 推荐:" + clothes)

# f-string 拼法(简单): 直接在 {} 里放变量
print(f"{name} 推荐了 {clothes}, 只要 {price} 元")

# 还能做简单计算
print(f"打8折后: {price * 0.8} 元")

# 这就是你文案脚本里那行的原理:
prod = "黑色皮衣"
print(f"产品: {prod}")
