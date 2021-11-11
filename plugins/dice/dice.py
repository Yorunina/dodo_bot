from pyparsing import *
#import api
import random

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

#掷骰表达式解析，属于step4
class Roll_Analysis():
    def __init__(self, expr):
        self.expr = expr
        return
    #通过遍历来解析当前表达式中的层递关系
    def solve(self):
        expr = self.expr
        node_d = None
        #如果已经确定了是掷骰表达式，就会进来被遍历一通
        for i in range(0,len(expr)):
            #如果当前位置是数字
            if expr[i].isdigit():
                #没啥好干的
                continue
            elif expr[i] == "d":
                #如果有d，则以d为中心前后瞻仰来建立节点Node_d
                if node_d:
                    #如果已经存在节点，就让节点结算，把他的结果作为投掷面数
                    times = node_d.result
                elif i-1 < 0:
                    #如果处在第一位，则为省略前值1
                    times = 1
                elif expr[i-1].isdigit():
                    #如果是数字，那就规整
                    times = int_reform(expr[i-1], 1, 1000)
                else:
                    #如果啥都不是，那就是默认值
                    times = 1
                if i+1 >= len(expr):
                    #如果处于最后一位，则省略后值，默认头
                    ceil = roll_ceil
                elif expr[i+1].isdigit():
                        #如果是数字，那就规章
                        ceil = int_reform(expr[i+1], 1, 100000)
                else:
                    #不然默认
                    ceil = roll_ceil
                node_d = Node_d(times, ceil, 1)
                #按照数据建立节点Node_d
            elif expr[i] == "b":
                #如果检查当前位是b
                #特殊符号必须作为node_d的属性出现
                if i+1 >= len(expr):
                    times = 1
                elif expr[i+1].isdigit():
                    times = int_reform(expr[i+1], 1,10)
                else:
                    times = 1
                if node_d:
                    #检查是否有已经存在的节点，如果有，就计算
                    node_d.b_cal(times)
                else:
                    #如果没有，按照默认值新建然后计算
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
        return node_d.result_str, node_d.result

#建立节点，属于step4中的小内容
class Node_d:
    def __init__(self, times = 1, ceil = 100, floor = 1):
        self.d_times, self.d_ceil, self.d_floor = int(int_reform(times, 1 , 1000)), int(ceil), int(floor)
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
        self.random_list = self.random_list[-times:]
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

#万恶之源对象
class Dice:
    def __init__(self, dice_ori_str):
        self.dice_expr = dice_ori_str
        self.expr = self.roll_parsing()
        self.expr_str = self.expr
        return


#初始化Dice对象的时候就会执行这个，属于step0
    def roll_parsing(self):
        #这里用于解析掷骰表达式
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


    #表达式计算，这相当于掷骰表达式解析的入口函数，属于step1
    def expr_cal(self):
        res_str, res = self.travers(self.expr)
        #这三个返回分别是，第一个给用户看的，第二个给用户看的，第三个给用户看的
        return self.dice_expr, res_str, res

    #多深度遍历，入口下面就是这玩意，属于是step2
    def travers(self, expr):
        #傻逼了，不用深拷贝
        expr_str = list(expr)
        for i in range(0,len(expr)):
            row = expr[i]
            if isinstance(row, list):
                #如果当前位置是列表，就往下深入一层
                ans_str, ans = self.travers(row)
                expr[i] = ans
                #字符串和结果都要记一下
                expr_str[i] = ans_str
        #对于当前深度的列表进行综合计算
        res_str, res = self.single_expr_cal(expr, expr_str)
        #返回值用来迭代
        return res_str, res

    #表达式计算，属于step3
    def single_expr_cal(self, expr:list, expr_str):
        for i in range(0, len(expr)):
            #查询是否为掷骰式，含有下列元素则说明其符合
            if expr[i] in ["d","p","k","q","b"]:
                #掷骰表达式都给我进step4被解析
                res_str, res = Roll_Analysis(expr).solve()
                return res_str, res
        #普通列表表达式转结果
        res_str = "".join(map(str,expr))
        #ans如果是数字，其会经过eval导致变为int
        res = str(eval(res_str))
        expr_str = "".join(expr_str)
        return expr_str, res



ori_expr, res_str, res = Dice("dd+2dp").expr_cal()
print("{}={}={}".format(ori_expr, res_str, res))






class Card:
    def __init__(self):

        return
    def turn_attr(self, ori_str):
        #.st力量50. . .
        return