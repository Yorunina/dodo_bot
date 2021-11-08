import api
import requests
import json

class yiyan:
    def send_yiyan(msg):
        url = "https://v1.hitokoto.cn/"
        data = json.loads(requests.get(url).text)
        msg.send_refer(data["hitokoto"] + "\n——" +data["from"])
        return

class plugin_load:
#匹配类型：私聊、匹配依据：setu、调用函数：send_setu、匹配方式：前缀匹配：prefix、匹配优先级：50（越大越优先）
    def __init__(self):
        api.match_update('group', 'yy', yiyan.send_yiyan, 'pre', 50)
        return

if __name__ != "__main__":
    plugin_load()