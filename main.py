import api
import threading
import re
import time
match_map = api.get_match_map()
config = api.get_config()
# 轮询线程
class LoopTimer(threading.Timer):
    def __init__(self, interval, function, args=[], kwargs={}):
        threading.Timer.__init__(self, interval, function, args, kwargs)

    def run(self):
        api.extend_token()
        start_time = time.time()
        while True:
            self.finished.wait(self.interval)
            #一天一刷，身体健康
            if time.time() - start_time > 86400:
                start_time = time.time()
                api.extend_token()
            if self.finished.is_set():
                self.finished.set()
                break
            self.function(*self.args, **self.kwargs)


# 初始化平台以及api

def flow_filter(msg):
    content = msg.content
    # 多匹配机制
    if content.startswith(('.', '。')):
        # 清除空格和首位
        msg.command = content[1:].strip()
    return msg


def flow_deal(msg, flow):
    for obj in flow:
        key = obj['key']
        # 进行正则匹配
        if obj['match_type'] == 'reg':
            # 正则表达式匹配
            match_obj = re.match(key, msg.command, re.M | re.I)
            # 如果成功
            if match_obj:
                # 调用函数
                obj['function'](msg)
                break
        # 进行完全匹配
        if obj['match_type'] == 'abs' and msg.command == key:
            obj['function'](msg)
            break
        # 进行前缀匹配
        if obj['match_type'] == 'pre' and msg.command.lower().startswith(key):
            obj['function'](msg)
            break
    return


# 匹配流机制
def match_process(ori_msg):
    msg = api.Msg(ori_msg)
    print("\033[37mINFO : 收到来自{0}在频道{1}的消息：{2}\033[0m".format(
        msg.nickName, msg.channelId, msg.content if msg.content else msg.image))
    print("\033[32mDEBUG : %s\033[0m" % ori_msg)
    msg = flow_filter(msg)
    if msg.command:
        if msg.command == "reload":
            api.Plugin()
        try:
            flow_deal(msg, match_map['group'])
        except:
            raise"匹配时出现错误：" + Exception
    return


def main_loop():
    global config
    # 遍历获取群消息
    for group in config.group_list:
        msg_list = api.get_group_new_msg(group)
        # 记录新的时间锁
        new_ts = config.ts_lock[group]
        for msg in msg_list:
            # 比对时间锁刷新消息列表
            # 屁，没createTime。用id大小判断吧
            if msg["id"] > config.ts_lock[group]:
                # 将获取到的消息送入匹配序列
                # 比对id和之前id的大小，更新时间锁
                new_ts = msg["id"]
                msg["group"] = group
                # print(msg)
                # 创建匹配线程送入后续处理
                match_loop = threading.Thread(target=match_process, args=[msg])
                match_loop.start()
            else:
                continue
        # 进行时间锁的更新
        config.ts_lock[group] = new_ts
    return


if __name__ == "__main__":
    t = LoopTimer(2.5, main_loop)
    t.start()
