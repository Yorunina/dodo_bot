import json
import os
import random
import re
import dice
import copy

class Deck:
    def __init__(self):
        self.deck_file_name = []
        self.deck = {}
        #temp deck用于存储非重取出数据
        self.temp_deck = {}
        self.deck_file = './config/dice/deck/'
        self.load_dir()
        return

    def load_dir(self):
        #加载牌堆目录
        for filename in os.listdir(self.deck_file):
            #遍历文件名称
            if not filename.endswith(".json"):
                continue
            #符合条件的就插进去
            print(filename)
            self.load_deck(filename)
            #删掉尾缀，方便检索
            self.deck_file_name.append(filename.rstrip(".json"))
        return

    def load_deck(self, filename:str):
        #开文件，让我康康
        with open(self.deck_file + filename,'r',encoding='utf8') as fp:
            json_data = json.load(fp)
            for key, value in json_data.items():
                #把所有牌堆的条目存到一个字典里面
                if key not in self.deck:
                    self.deck[key] = value
                else:
                    self.deck[key] = self.deck[key] + value
        return
    
    def next_get(self, match) ->str:
        #这个啊，这个用来返回下一层的牌堆获取结果

        deck_name = match.group(1)
        if deck_name.startswith("%"):
            deck_name = deck_name[1:]
            no_repeat = True
        else:
            no_repeat = False
        return self.get(deck_name, no_repeat)

    def roll_cal(self, match) ->str:
        #这个用来解析roll表达式
        ori_expr, res_str, res = dice.Dice(match.group(1)).expr_cal()
        return res

    def get(self, deck_name, no_repeat = False):
        if deck_name in self.deck:
            #如果存在该牌堆，那么就读取json
            if (deck_name in self.temp_deck) and no_repeat:
                #如果已经存在在非重列表中，且非重选择，那么就
                res_list = self.temp_deck[deck_name]
            else:
                res_list = self.deck[deck_name]
            #权重分配
            deck_weight = []
            if len(res_list)!=0:
                pass
            elif no_repeat:
                res_list = self.deck[deck_name]
                print(deck_name)
                print(self.deck[deck_name])
            else:
                return ""
            for i in range(0, len(res_list)):
                #进行权重匹配
                #正则，头匹配，取出可能存在的权重
                re_deck_weight = re.match('::(\d+)::', res_list[i], flags=re.I|re.M)
                if re_deck_weight:
                    #如果存在权重，那么分配对应的数字
                    deck_weight.append(int(re_deck_weight.group(1)))
                else:
                    #否则就认为是1
                    deck_weight.append(1)
            #在已知权重的情况下，进行随机取出
            #从已知序列里面取数值，然后再从列表取，这样可以保留Index，以进行非重的删除
            ran_num_get = random.choices(range(0, len(deck_weight)), deck_weight, k=1)
            ran_num_get = ran_num_get[0]
            if no_repeat:
                ran_deck_get = res_list[ran_num_get]
                #这傻逼深拷贝规则什么时候能x啊？
                self.temp_deck[deck_name] = copy.deepcopy(res_list)
                del self.temp_deck[deck_name][ran_num_get]
            else:
                ran_deck_get = res_list[ran_num_get]
            #三个步骤
            #替换出下一层的牌堆
            next_deck = re.sub("\{(%?[^\}]+)\}", self.next_get, ran_deck_get, flags=re.I|re.M)
            #替换出掷骰表达式
            next_deck = re.sub("\[([^\}]+)\]", self.roll_cal, next_deck, flags=re.I|re.M)
            #替换掉可能存在的权重符号
            next_deck = re.sub("::\d+::\s*", "", next_deck, flags=re.I|re.M)
            if no_repeat:
                self.temp_deck.pop(deck_name)
            return next_deck
        else:
            return ""

deck = Deck()
print(deck.get(deck_name = "麻将对局"))
print(deck.get(deck_name = "高考合约"))