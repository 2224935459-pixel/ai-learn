# 函数 def: 给一段代码起个名, 需要时喊名字就跑
# 格式: def 名字():
#        缩进的代码(这个函数要做的事)

def say_hi(name):
    print(f"你好, {name}!")

# 喊名字调用它, 括号里传进去的值会填到 name
say_hi("江少")
say_hi("鸭子")

# 函数还能"返回"结果给你用
def make_tag(cloth):
    return f"#{cloth}"

tag = make_tag("皮衣")
print(tag)
