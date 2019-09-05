#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import re
# 好友功能
import utils.weather as weather
import utils.metro_timetable as metro
import utils.lunar as lunar
import utils.music_platform as music


def auto_accept_friends(msg):
    """自动接受好友"""
    # 接受好友请求
    new_friend = msg.card.accept()
    # 向新的好友发送消息
    new_friend.send('既然你这么喜欢我，想加我为好友，那我就勉为其难的接受吧~')
    new_friend.send('我现在支持查询城市天气\r\n你可以试试“tq北京”\r\n目前仅支持城市级别的实时天气')
    new_friend.send('我现在还可以查询当天的黄历信息\r\n你可以试试“hl”获取当天的黄历')
    new_friend.send('当然如果有什么其他需求，也可以告诉我，尽量满足呢~')


def auto_reply(msg):
    """自动回复"""
    # 关键字回复
    keyword_reply(msg)


def handle_system_msg(msg):
    """处理系统消息"""
    raw = msg.raw
    # 4表示消息状态为撤回
    if raw['Status'] == 4 and msg.bot.is_forward_revoke_msg:
        # 转发撤回的消息
        forward_revoke_msg(msg)


def forward_revoke_msg(msg):
    """转发撤回的消息"""
    # 获取被撤回消息的ID
    revoke_msg_id = re.search('<msgid>(.*?)</msgid>', msg.raw['Content']).group(1)
    # bot中有缓存之前的消息，默认200条
    for old_msg_item in msg.bot.messages[::-1]:
        # 查找撤回的那条
        if revoke_msg_id == str(old_msg_item.id):
            # 判断是群消息撤回还是好友消息撤回
            if old_msg_item.member:
                sender_name = '群「{0}」中的「{1}」'.format(old_msg_item.chat.name, old_msg_item.member.name)
            else:
                sender_name = '「{}」'.format(old_msg_item.chat.name)
            # 名片无法转发
            if old_msg_item.type == 'Card':
                sex = '男' if old_msg_item.card.sex == 1 else '女' or '未知'
                msg.bot.master.send('「{0}」撤回了一张名片：\n名称：{1}，性别：{2}'.format(sender_name, old_msg_item.card.name, sex))
            else:
                # 转发被撤回的消息
                old_msg_item.forward(msg.bot.master, prefix='{}撤回了一条{}：'.format(sender_name, get_msg_chinese_type(old_msg_item.type)))
            return None


def get_msg_chinese_type(msg_type):
    """转中文类型名"""
    if msg_type == 'Text':
        return '文本'
    if msg_type == 'Map':
        return '位置'
    if msg_type == 'Card':
        return '名片'
    if msg_type == 'Note':
        return '提示'
    if msg_type == 'Sharing':
        return '分享'
    if msg_type == 'Picture':
        return '图片'
    if msg_type == 'Recording':
        return '语音'
    if msg_type == 'Attachment':
        return '文件'
    if msg_type == 'Video':
        return '视频'
    if msg_type == 'Friends':
        return '好友请求'
    if msg_type == 'System':
        return '系统'


def keyword_reply(msg):
    """关键字回复"""
    text = msg.text.lower()
    if text.startswith('tq') or text.startswith("天气"):
        info = tq_info(text, 'tq')
        return msg.reply(info)
    # elif text.startswith('dt'):
    #     info = dt_info(text, 'dt')
    #     return msg.reply(info)
    elif text == 'hl' or text == "huangli" or text == "黄历":
        info = lunar.get()
        return msg.reply(info)
    # elif text.startswith('mc'):
    #     info = mc_info(text, 'mc')
    #     return msg.reply(info)
    elif text == '老公':
        return msg.reply("老公在呢~")
        pass
    elif text.startswith("tp"):
        return msg.reply("现实世界不允许传送！")
    elif text == "在么":
        return msg.reply("不借钱，不随份子")


def tq_info(text, tag):
    dm = text.lstrip(tag).strip()
    if len(dm) > 0:
        info = weather.get(dm)
        return info
    return '整错啦，想好啦要说啥'


def dt_info(text, tag):
    dm = text.lstrip(tag).strip()
    if len(dm) > 0:
        dms = dm.split(' ')
        if len(dms) == 2:
            info = metro.get(dms[0], dms[1])
            return info
        if len(dms) == 1:
            info = metro.get(dms[0], '')
            return info
    return '输入格式不正确'


def mc_info(text, tag):
    dm = text.lstrip(tag).strip()
    if len(dm) > 0:
        info = music.get(dm)
        return info
    return '输入格式不正确'
