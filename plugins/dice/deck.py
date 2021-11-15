import json
import os
import random
import re
import roll

class Deck:
    def __init__(self):
        self.deck_file_name = []
        self.deck_search_list = {}
        self.deck = dict()
        #temp deck用于存储非重取出数据
        self.poss_deck = {}
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
            #采用惰加载，不插了，有需要的再插
            #self.load_deck(filename)
            #删掉尾缀，方便检索
            re_filename = filename.rstrip(".json")
            #加载文件中的所有key储存到可检索表中
            with open(self.deck_file + filename,'r',encoding='utf8') as fp:
                json_data = json.load(fp)
                for key, value in  json_data.items():
                    #把所有可用的牌堆名称与文件名进行字典映射
                    self.deck_search_list[key] = filename
            self.deck_file_name.append(re_filename)
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
        return self.tra_get(deck_name, no_repeat)

    def roll_cal(self, match) ->str:
        #这个用来解析roll表达式
        ori_expr, res_str, res = roll.Dice(match.group(1)).expr_cal()
        return res

    def get(self, deck_name):
        self.poss_deck = {}
        return self.tra_get(deck_name)

    def tra_get(self, deck_name, no_repeat = False):
        if deck_name in self.deck:
            flag = True
        elif deck_name in self.deck_search_list:
            self.load_deck(deck_name + ".json")
            flag = True
        else:
            return ""
            #如果存在该牌堆，那么就读取json
        if flag:
            res_list = self.deck[deck_name]
            if deck_name in self.poss_deck:
                #如果已经存在概率表，且目前为非重状态
                #则当前概率列表为概率存储中的内容
                poss_list = self.poss_deck[deck_name]
                if sum(poss_list) == 0:
                    poss_list = []
            else:
                #否则就获取一个新的概率表
                self.poss_deck[deck_name] = []
                poss_list = []

            if poss_list == []:
                for i in range(0, len(res_list)):
                    #进行权重匹配
                    #正则，头匹配，取出可能存在的权重
                    re_deck_weight = re.match('::([d\+\-\*/\d]+)::', res_list[i], flags=re.I|re.M)
                    if re_deck_weight:
                        #如果存在权重，那么分配对应的数字
                        poss_list.append(int(self.roll_cal(re_deck_weight)))
                    else:
                        #否则就认为是1
                        poss_list.append(1)
                self.poss_deck[deck_name] = poss_list
            #在已知权重的情况下，进行随机取出
            #从已知序列里面取数值，然后再从列表取，这样可以保留Index，以进行非重的删除
            ran_num_get = random.choices(range(0, len(poss_list)), poss_list, k=1)
            ran_num_get = ran_num_get[0]
            if no_repeat:
                self.poss_deck[deck_name][ran_num_get] -= 1
            ran_deck_get = res_list[ran_num_get]
            #三个步骤
            #替换出下一层的牌堆
            next_deck = re.sub("\{(%?[^\}]+)\}", self.next_get, ran_deck_get, flags=re.I|re.M)
            #替换出掷骰表达式
            next_deck = re.sub("\[([^\}]+)\]", self.roll_cal, next_deck, flags=re.I|re.M)
            #替换掉可能存在的权重符号
            next_deck = re.sub("::([d\+\-\*/\d]+)::\s*", "", next_deck, flags=re.I|re.M)

            return next_deck


    def deck_get(msg):
        re_command = re.match("draw\s*(.+)", msg.command, re.M | re.I)
        command = re_command.group(1)
        content = deck.self.tra_get(command)
        msg.send(content)
        return


if __name__ != "__main__":
    deck = Deck()