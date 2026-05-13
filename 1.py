import math


# import copy as cp

# yes_votes=42_572_654


# print("yes_votes:",yes_votes)

# print(2/2)

# print(6//4)


# n = 6
# d = 4
# result = (6 +4 - 1) // 4
# print(result)

# mydata=[1,2,3,4,5]
# mydata2=mydata[:]
# copyData = cp.copy(mydata)
# print("copyData",copyData)

# # i=0
# # while(i<10):
# #     i=i+1
# #     print(i,end=",")

# print((-3)**2)

# x = int(input("Please enter an integer: "))

# list=["张三","李四","王五"]

# for w in list:
#     print(w,len(w))

# a=list(range(0,101,10))


# print(a)

# class Point:
#     def __init__(self,x:int,y:int):
#         self.x=x
#         self.y=y
#     def getArea(self):
#         return  self.x * self.y

# p=Point(5,10)

# print(p.getArea())

# pairs = [(1, "one"), (2, "two"), (3, "three")]

# pairs2=list(map(lambda a:a[1], pairs))

# print("pp==>", pairs2)

# pairs3=[num for (num,word) in pairs]
# print(pairs3)

# objList=[{"name":"张三","age":"18"},{"name":"李四","age":"20"}]

# print("objList",objList)
# for i in objList:
#     del i['age']


# print("objList2",objList)

# newList=[item["name"] for item in objList]

# print("newList",newList)

# pairs = [(1, "one"), (2, "two"), (3, "three")]
# pairs2 = list(map(lambda a: a[1], pairs))   # 取出每个元组的第二个元素
# print(pairs2)  # ['one', 'two', 'three']


# def f(ham: str, str="world") -> int:

#     return ham + str


# print(f("hello "))

# list = [1, 2, 3, 4, 5, 6, 1]

# list.extend([7, 8, 9])

# list.insert(0, 0)
# index = list.index(1, 3)
# print("index", index)

# squares = [
#     x**math.pi
#     for x in range(
#         1,
#         10,
#     )
# ]
# print("squares", squares)


# f = [fruit.strip() for fruit in [" apple ", " banana "]]


# print("f ", f)


# list = [round(math.pi, i) for i in range(1, 10)]

# print("list", list)

# names = ["Alice", "Bob", "Charlie"]
# scores = [85, 92, 78]

# # 打包成 (name, score) 元组对
# pairs = zip(
#     names,
#     scores,
# )  # 迭代器对象
# print(list(pairs))  # [('Alice', 85), ('Bob', 92), ('Charlie', 78)]
# t = 1, 3, 4, "hello"
# print(t.count(1))

# matrix = [
#     [1, 2, 3, 4],
#     [5, 6, 7, 8],
#     [9, 10, 11, 12],
# ]

# newList = [[row[i] for row in matrix] for i in range(0, 3)]
# print(newList)

# flat = [num for row in matrix for num in row]

# print(flat)

# str = [1, 2] * 2

# print(str)

# a = [1, 2, 2, 5, 5, 5, 5, 6, 9, 1]

# # a2 = [x for x in a if x >= 3]
# # print("a2", a2)

# for index in range(len(a) - 1, -1, -1):
#     if a[index] < 3:
#         del a[index]
# print(a)

# a = {"张三", "李四", "王五", "张三"}
# b = {"张三", "赵高", "白涛涛"}
# c = set(["张三", "王二"])

# print(a)
# print(a & b)
# print(a | b)
# print(a ^ b)
# print(c & a & b)

# str1 = str(input())

# list1 = str1.split()[3:]

# print(list1)


# my_list = ["P", "y", "t", "h", "o", "n"]
# list2 = sorted(my_list)
# print(list2)
# print(my_list)
# my_list.sort(reverse=True)
# print(my_list)
# name = ["Niumei", "YOLO", "Niu Ke Le", "Mona"]


# food = ["pizza", "fish", "potato", "beef"]
# number = [3, 6, 0, 3]
# friends = []

# for item in [name, food, number]:
#     print(item)
# str1 = input()
# str2 = input()

# print(int(str1) & int(str2))
# print(int(str1) | int(str2))
# print(bin(100))

# current_users = ["Niuniu", "Niumei", "GURR"]
# new_users = ["GurR", "Niu Ke Le", "Tuo Rui Chi'"]

# lls = [x.lower() for x in current_users]
# for key in new_users:
#     if key in lls:
#         print(
#             f"The user name {key} has already been registered! Please change it and try again!"
#         )
#     else:
#         print(f"Congratulations, the user name {key} is available!")

# print("张三李四王五麻子".find("麻子1"))


g = {
    "A": 4.0,
    "B": 3.0,
    "C": 2.0,
    "D": 1.0,
    "F": 0,
}

num1 = 0
num2 = 0
while True:
    s1 = input()
    if s1 == "False":
        break
    else:
        s2 = input()
        print("s2", s2)
        num1 += g[s1] * int(s2)
        num2 += int(s2)

print(format(num1 / num2, ".2f"))
