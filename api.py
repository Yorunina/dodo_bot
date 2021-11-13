import requests
import json
import configparser
import uuid
from io import BytesIO
from PIL import Image
import os, sys
from importlib import import_module

global_dict = {}
match_map ={'private':[],
            'group':[]}

#进行全局变量管理
def glo_set(key, value):
    global_dict[key] = value
    return
def glo_get(key, defValue = None):
    try:
        return global_dict[key]
    except KeyError:
        return defValue

#HTTP POST API集合，太多了，鬼写注释
def api_http(url, req):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {"uid": config.uid, "token": config.token,
               "clientType": config.clientType}
    payload.update(req)
    res = requests.post(url, headers=headers, timeout=2, data=payload)
    return res.text

def extend_token():
    res = api_http(
        "https://apis.mahuatalk.com/island/api/beta/@me/extend-my-life", {})
    data = json.loads(res)
    return data["data"]["token"]


def refresh_token():
    res = api_http(
        "https://apis.mahuatalk.com/island/api/beta/@me/request-new-token", {})
    data = json.loads(res)
    return data["data"]["token"]


def get_group():
    res = api_http(
        "https://apis.mahuatalk.com/island/api/beta/islands", {})
    data = json.loads(res)
    return data["data"]["islands"]


def get_channels(islandId):
    res = api_http(
        "https://apis.mahuatalk.com/island/api/beta/channels", {"islandId": islandId})
    data = json.loads(res)
    return data["data"]["channels"]


def get_channel_msg(channelId, size):
    res = api_http("https://apis.mahuatalk.com/island/api/beta/messages",
                        {"channelId": channelId, "size": size})
    data = json.loads(res)
    return data["data"]["messages"]


def get_group_new_msg(islandId):
    res = api_http(
        "https://apis.mahuatalk.com/island/api/beta/messages/batch", {"islandId": islandId})
    data = json.loads(res)
    return data["data"]["messages"]


def send_msg(channelId, type, content, resourceJson=None, referencedMessageId=None):
    tk = str(uuid.uuid4())
    if type == 1:
        payload = {"channelId": channelId,
                   "type": type, "content": content, "tk": tk}
    elif type == 2:
        payload = {"channelId": channelId, "type": type,
                   "resourceJson": json.dumps(resourceJson),  "tk": tk}
    if referencedMessageId:
        payload["referencedMessageId"] = referencedMessageId
    res = api_http(
        "https://apis.mahuatalk.com/island/api/beta/messages/send", payload)
    data = json.loads(res)
    return data

def send_chat(islandId, toUid, type, content, resourceJson=None):
    tk = str(uuid.uuid4())
    if type == 1:
        payload = {"islandId": islandId, "toUid": toUid,
                       "type": type, "content": content, "tk": tk}
    elif type == 2:
        payload = {"islandId": islandId, "toUid": toUid,
                   "type": type, "resourceJson": resourceJson,  "tk": tk}
    res = api_http(
        "https://apis.mahuatalk.com/island/api/beta/chat/send", payload)
    data = json.loads(res)
    return data

def get_channel_msg(islandId, toUid, nickName):
    res = api_http("https://apis.mahuatalk.com/island/api/beta/member/nickname/edit",
                        {"islandId": islandId, "toUid": toUid, "nickName": nickName})
    data = json.loads(res)
    return data

#配置文件初始化
class ConfigInit:
    def __init__(self):
        self.ts_lock = {}

    def config_init(self):
        try:
            config = configparser.ConfigParser()
            config.read("./config/account.ini")
            secs = config.sections()
            if "bot" not in secs:
                # 添加不存在的配置节并初始化
                config.add_section("bot")
                config.set("bot", "uid", "")
                config.set("bot", "token", "")
                config.set("bot", "clientType", "3")
                # 写入配置文件
                f = open('./config.ini', 'w')
                config.write(f)
                f.close()

            opt = config.options("bot")
            if "uid" not in opt:
                config.set("bot", "uid", "")
                f = open('./config.ini', 'w')
                config.write(f)
                f.close()
            if "token" not in opt:
                config.set("bot", "token", "")
                f = open('./config.ini', 'w')
                config.write(f)
                f.close()
            self.uid = config.get("bot", "uid")
            self.token = config.get("bot", "token")
            self.clientType = 3
        except:
            print("初始化错误！")
            raise
        return
    def group_init(self):
        # 初始化群列表
        self.group_list = [108193]
        if self.group_list:
            for group in self.group_list:
                # 初始化时间锁
                # self.ts_lock.update({group:time.time()*1000})
                # 没createId，判断他妈
                # 生成初始依据id
                self.ts_lock[group] = 0
                return

#初始化配置
config = ConfigInit()
config.config_init()
config.group_init()
#定义全局获取方式
def get_config():
    return config

#对msg进行自行分类初始化
class Msg:
    def __init__(self, msg):
        self.id = msg["id"]
        self.channelId = msg["channelId"]
        self.from_uid = msg["uid"]
        self.content = msg["content"] if "content" in msg else None
        self.command = None
        self.nickName = msg["nickName"]
        #提取可能的image url
        self.image = msg["resourceJson"] if msg["resourceJson"] else None
        #提取可能的at信息
        self.mentionTargetsJson = msg["mentionTargetsJson"]
        #提取可能的回复信息
        if "referencedMessage" in msg:
            self.referencedMessage = msg["referencedMessage"]
        else:
            self.referencedMessage = None
    
    def send(self, content = None, image_url = None):
        if content:
            send_msg(self.channelId, 1, content)
        if image_url:
            #获取图片尺寸
            response = requests.get(image_url)
            image = BytesIO(response.content)
            (width, height) = Image.open(image).size
            resourceJson = {"resourceType" : 1,"useType" : 1,"width" : width,"height" : height,"resourceUrl" : image_url}
            send_msg(self.channelId, 2, None, resourceJson = resourceJson)
    
    def send_refer(self, content = None, image_url = None):
        if content:
            send_msg(self.channelId, 1, content, resourceJson = None, referencedMessageId = self.id)
        if image_url:
            #获取图片尺寸
            response = requests.get(image_url)
            image = BytesIO(response.content)
            (width, height) = Image.open(image).size
            resourceJson = {"resourceType" : 1,"useType" : 1,"width" : width,"height" : height,"resourceUrl" : image_url}
            send_msg(self.channelId, 2, None, resourceJson = resourceJson, referencedMessageId = self.id)


#更新匹配结构
def match_update(msg_type: str, key: str, fun: str, match_type = 'reg', priority = 100):
    #优先级越大越优先，默认为100
    #match_map本身类型为承载msg_type触发类型的字典
    #msg_type下则为一个依照优先级顺序排序的列表
    #列表中每个元素对应不同回复的属性字典
    content = {'match_type':match_type, 'key':key, 'function':fun, 'priority':priority}
    if content not in match_map[msg_type]:
        index = -1
        for i in range(0, len(match_map[msg_type])-1):
            #每次插入进行一次独立排序，得到优先级队列
            if match_map[msg_type][i]['priority'] < priority:
                index = i
                break
        match_map[msg_type].insert(index, content)
        print("已导入: %s 的回复" % (key))
    return

#匹配表获取
def get_match_map():
    print(match_map)
    return match_map

#插件初始化
class Plugin:
    def __init__(self):
        self.load_dir()

    def load_dir(self):
        for filename in os.listdir("plugins"):
            if not filename.endswith(".zip"):
                continue
            self.load_Plugin(filename)

    def load_Plugin(self, filename:str):
        pluginPath = os.path.join("plugins", filename)
        sys.path.append(pluginPath)
        name = filename.rsplit(".", 1)[0]
        try:
            module = import_module(name)
        except Exception as r:
            print("插件" + name + "载入出错！" + r)
            return
        print("载入插件%s成功"%name)
        return module

Plugin()