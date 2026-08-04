# 对比: 列表只是装数据(不动), for 才是重复干活的
products = ["黑色皮衣", "碎花连衣裙", "针织开衫"]

print("=== 列表自己啥也不干, 只是被打印 ===")
print(products)

print("=== for 在循环: 每圈都真的调一次'模拟大模型' ===")
for p in products:
    # 下面这两行是'对每个产品做的事', for 自动跑3遍
    fake_reply = f"[AI写了关于{p}的文案]"
    print(fake_reply)
