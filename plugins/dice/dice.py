from unittest import result
from pyparsing import *
#import api
import sqlite3
import random
import re

roll_ceil = 100


def int_reform(num ,min, max):
    #取整
    num = round(int(num))
    if num>=min and num<=max:
        return str(num)
    elif num<min:
        raise Exception("超出有效下值范围")
    elif num>max:
        raise Exception("超出有效上值范围")


class Roll_Analysis():
    def __init__(self, expr):
        self.expr = expr
        return
    #通过遍历来解析当前表达式中的层递关系
    def travers(self):
        expr = self.expr
        node_d = None
        for i in range(0,len(expr)):
            if expr[i].isdigit():
                continue
            elif expr[i] == "d":
                if node_d:
                    times = node_d.result
                elif i-1 < 0:
                    times = 1
                elif expr[i-1].isdigit():
                    times = int_reform(expr[i-1], 1, 100)
                else:
                    times = 1
                if i+1 >= len(expr):
                    ceil = roll_ceil
                elif expr[i+1].isdigit():
                        ceil = int_reform(expr[i+1], 1, 100000)
                else:
                    ceil = roll_ceil
                node_d = Node_d(times, ceil, 1)
            elif expr[i] == "b":
                if i+1 >= len(expr):
                    times = 1
                elif expr[i+1].isdigit():
                    times = int_reform(expr[i+1], 1,10)
                else:
                    times = 1
                if node_d:
                    node_d.b_cal(times)
                else:
                    node_d = Node_d(1, roll_ceil, 1)
                    node_d.b_cal(times)
            elif expr[i] == "p":
                if i+1 >= len(expr):
                    times = 1
                elif expr[i+1].isdigit():
                    times = int_reform(expr[i+1], 1,10)
                else:
                    times = 1
                if node_d:
                    node_d.p_cal(times)
                else:
                    node_d = Node_d(1, roll_ceil, 1)
                    node_d.p_cal(times)
            elif expr[i] == "k":
                if i+1 >= len(expr):
                    times = 1
                elif expr[i+1].isdigit():
                    times = int_reform(expr[i+1], 1,100)
                else:
                    times = 1
                if node_d:
                    node_d.k_cal(times)
                else:
                    node_d = Node_d(1, roll_ceil, 1)
                    node_d.k_cal(times)
            elif expr[i] == "q":
                if i+1 >= len(expr):
                    times = 1
                elif expr[i+1].isdigit():
                    times = int_reform(expr[i+1], 1,100)
                else:
                    times = 1
                if node_d:
                    node_d.q_cal(times)
                else:
                    node_d = Node_d(1, roll_ceil, 1)
                    node_d.q_cal(times)
        return node_d.result_str


class Node_d:
    def __init__(self, times = 1, ceil = 100, floor = 1):
        self.d_times, self.d_ceil, self.d_floor = int(times), int(ceil), int(floor)
        self.d_cal()
        return
    def d_cal(self):
        self.d_times, self.d_ceil, self.d_floor
        random_list = []
        for i in range(0, self.d_times):
            #插入单词的结果存储到列表中
            random_list.append(random.randint(self.d_floor, self.d_ceil))
        #这玩意保存所有的掷骰数据，免得你个逼仔小子要bpkq
        self.random_list = random_list
        self.d_list = random_list
        #还要给你个逼仔小子生成个str
        self.result_str = "+".join(map(str,random_list))
        #这玩意保存掷骰的和，当然，有些时候有bpkq，这只是d的和罢了
        self.result = sum(self.random_list)
        return

    def b_cal(self, times):
       #奖励骰
        times = int(times)
        self.b_times = times
        self.result_str = ""
        bonus_list = []
        str_list = []
        for i in range(0, len(self.random_list)):
            #这玩意用来记录我投了多少次奖励骰
            now_t = 0
            new_random = self.random_list[i]
            bonus_list = []
            #创建一个跟奖励骰挂钩的列表，来记录有什么奖励骰
            if new_random % 10 == 0:
                ceil = 10
                floor = 1
            else:
                ceil = 9
                floor = 0
            while now_t < times:
                now_random = random.randint(floor, ceil)
                bonus_list.append(now_random)
                if new_random > now_random * 10:
                    new_random = now_random * 10 + new_random % 10
                now_t = now_t + 1
            b_str_list = ",".join(map(str, bonus_list))
            str_list.append(str(self.random_list[i]) + "{Bonus:" + b_str_list + "}(" + str(new_random) + ")")
            self.random_list[i] = new_random
        self.result_str = str(self.d_times) + "D" + str(self.d_ceil) + "(" + ",".join(str_list) + "[" + "+".join(map(str, self.random_list)) + "])"
        self.result = sum(self.random_list)
        return

    def p_cal(self, times):
       #惩罚骰
        times = int(times)
        self.p_times = times
        self.result_str = ""
        bonus_list = []
        str_list = []
        for i in range(0, len(self.random_list)):
            #这玩意用来记录我投了多少次惩罚骰
            now_t = 0
            new_random = self.random_list[i]
            bonus_list = []
            #创建一个跟惩罚骰挂钩的列表，来记录有什么惩罚骰
            if new_random % 10 == 0:
                ceil = 10
                floor = 1
            else:
                ceil = 9
                floor = 0
            while now_t < times:
                now_random = random.randint(floor, ceil)
                bonus_list.append(now_random)
                if new_random < now_random * 10:
                    new_random = now_random * 10 + new_random % 10
                now_t = now_t + 1
            b_str_list = ",".join(map(str, bonus_list))
            str_list.append(str(self.random_list[i]) + "{Punish:" + b_str_list + "}(" + str(new_random) + ")")
            self.random_list[i] = new_random
        self.result_str = str(self.d_times) + "D" + str(self.d_ceil) + "(" + ",".join(str_list) + "[" + "+".join(map(str, self.random_list)) + "])"
        self.result = sum(self.random_list)
        return

    def k_cal(self, times):
        times = int(times)
        self.k_times = times
        self.result_str = ""
        #排序
        ori_list = self.random_list
        self.random_list.sort()
        self.random_list = self.random_list[-1-times:-1]
        self.result = sum(self.random_list)
        self.result_str = "{" + ",".join(map(str, ori_list)) + "}" + "[" + "+".join(map(str, self.random_list)) + "]" + "(" + str(self.result) + ")"
        return

    def q_cal(self, times):
        times = int(times)
        self.k_times = times
        self.result_str = ""
        #排序
        ori_list = self.random_list
        self.random_list.sort()
        self.random_list = self.random_list[0:times]
        self.result = sum(self.random_list)
        self.result_str = "{" + ",".join(map(str, ori_list)) + "}" + "[" + "+".join(map(str, self.random_list)) + "]" + "(" + str(self.result) + ")" 
        
        return

class Dice:
    def __init__(self, dice_ori_str):
        self.dice_expr = dice_ori_str
        return

    def roll_parsing(self):
        #这里用于解析掷骰表达式
        #此处用来解析括号
        num = Combine(Word(nums) + (Word(nums) + '.' + Word(nums))*(0,1))
        #定义了括号的匹配法则
        LPAR,RPAR = map(Suppress, '()')
        #用forward占位，以此来声明一个可以迭代的表达式类型
        expr = Forward()
        #factor代表最小因素，可以视为括号的内容或者单纯的数字
        #或者说，其为分组内容
        factor = num|Group(LPAR + expr + RPAR)
        d_factor= Group(factor[0,1] + OneOrMore(oneOf('d p b k q #') + factor[0,1]))|factor
        expr <<= d_factor + ZeroOrMore(oneOf('* / + -') + d_factor)
        return expr.parseString(self.dice_expr).as_list()

    #表达式计算
    def expr_cal(self, row:list):
        temp_row = row
        for i in range(0, len(row)):
            #查询是否为掷骰式，含有下列元素则说明其符合
            if row[i] in ["d","p","k","q","b"]:
                roll_ans = Roll_Analysis(row)
                self.roll_cal(roll_ans)
                break
        res = eval("".join(temp_row))

        return res

    #多深度遍历
    def travers(self):
        expr = self.roll_parsing()
        for i in range(0,len(expr)):
            row = expr[i]
            if isinstance(row, list):
                ans = self.travers(row)
                expr[i] = ans
        res = self.roll_cal(expr)
        return res

dice = Dice("")
print(Roll_Analysis(["3","d","100","q","2"]).travers())