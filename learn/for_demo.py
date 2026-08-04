# for 循环: 把列表里每个元素, 挨个取出来处理一遍
# 格式: for 临时名 in 列表:
#       缩进的代码(前面空4格) 会对每个元素跑一次

products = ["黑色皮衣", "碎花连衣裙", "针织开衫"]

# 对列表里每个产品, 都打印一次
for p in products:
    print(f"正在处理: {p}")

# 带编号的循环 (enumerate 自动给序号, 从0开始)
for i, p in enumerate(products):
    print(f"第{i+1}件: {p}")
