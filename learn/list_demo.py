# 列表 list: 一批数据放一个盒子里, 用 [] 包, 逗号隔开
# 编号从 0 开始: 第1个是 [0], 第2个是 [1] ...

products = ["黑色皮衣", "碎花连衣裙", "针织开衫"]

# 看整个列表
print(products)

# 拿第1个(编号0)
print(products[0])

# 拿第2个(编号1)
print(products[1])

# 数一下列表里有几个
print("共", len(products), "个")

# 用循环把每个都打印出来 (后面一课细讲, 先看效果)
for p in products:
    print(f"推荐: {p}")
