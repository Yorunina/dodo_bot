import json
import os
import random
import re


class Deck:
    def __init__(self):
        self.deck_file_name = []
        self.deck = {}
        self.deck_file = './config/dice/deck/'
        self.load_dir()
        return

    def load_dir(self):
        #加载牌堆目录
        for filename in os.listdir(self.deck_file):
            print(filename)
            #遍历文件名称
            if not filename.endswith(".json"):
                continue
            #符合条件的就插进去
            self.load_deck(filename)
            self.deck_file_name.append(filename.rstrip(".json"))
        return

    def load_deck(self, filename:str):
        with open(self.deck_file + filename,'r',encoding='utf8') as fp:
            json_data = json.load(fp)
            for key, value in json_data.items():
                if key not in self.deck:
                    self.deck[key] = value
                else:
                    self.deck[key] = self.deck[key] + value
        return
    
    def get(self, deck_name):
        if deck_name in self.deck:
            res_list = self.deck[deck_name]
            for i in range(0, len(res_list)):
                #进行权重匹配
                re.match('::', 'www.runoob.com').span()
                if 


deck = Deck()