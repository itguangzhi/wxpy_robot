#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import config as config
import utils.ap_scheduler as ap_scheduler
import utils.weather as weather
import ssl


def load_config_to_bot(bot):
    """加载配置项"""
    bot_status = '机器人登录成功！！！'
    # 未定义机器人管理员
    if not config.bot_master_name:
        bot.master = bot.file_helper
        bot_status += '\n未设置机器人管理员，信息将发送至文件助手，不能使用远程命令控制机器人！\n\n'
    else:
        master = search_friend(bot, config.bot_master_name)
        # 查找管理员
        if master:
            bot.master = master
            bot_status += '\n机器人管理员成功设置为：「{0}」，这里查看管理员命令手册->' \
                          'https://github.com/pig6/wxrobot\n\n'.format(config.bot_master_name)
        else:
            bot.master = bot.file_helper
            bot_status += '\n在好友列表中未找到名为「{}」的好友，信息将发送至文件助手，不能使用远程命令控制机器人！\n\n'.format(
                config.bot_master_name)
    # 设置开关
    bot.is_friend_auto_reply = config.is_friend_auto_reply
    bot.is_group_reply = config.is_group_reply
    bot.is_group_at_reply = config.is_group_at_reply
    bot.is_listen_friend = config.is_listen_friend
    bot.is_forward_mode = config.is_forward_mode
    bot.is_listen_sharing = config.is_listen_sharing
    bot.is_forward_revoke_msg = config.is_forward_revoke_msg
    # 加载对应好友和群
    load_listen_friend(bot)
    load_forward_groups(bot)
    load_listen_sharing_groups(bot)
    # 每天定时提醒
    ap_scheduler.timely_execute(load_timely_remind, config.timing_hour, config.timing_minute, args=[bot])
    # 发送机器人状态信息
    bot_status = bot_status if '文件助手' in bot_status else bot_status + bot_status_detail(bot)
    bot.master.send(bot_status)


def load_listen_friend(bot):
    """加载需要监听的人和群"""
    if bot.is_listen_friend:
        if len(config.listen_friend_names):
            bot.listen_friends = search_friends(bot, config.listen_friend_names)
            if not bot.listen_friends:
                bot.listen_friends = []
                bot.is_listen_friend = False
                return '未在好友中找到备注为「{}」的监听对象！'.format(str(config.listen_friend_names))
        else:
            bot.listen_friends = []
        if len(config.listen_friend_groups):
            bot.listen_friend_groups = search_groups(bot, config.listen_friend_groups)
            if not len(bot.listen_friend_groups):
                bot.listen_friend_groups = []
                bot.is_listen_friend = False
                return '未找到群名包含「{}」的监听群！'.format(config.listen_friend_groups)
        else:
            bot.listen_friend_groups = []
    return None


def load_forward_groups(bot):
    """加载需要转发的群"""
    if bot.is_forward_mode:
        bot.forward_groups = search_groups(bot, config.forward_groups)
        if not len(bot.forward_groups):
            bot.forward_groups = []
            bot.is_forward_mode = False
            return '未找到群名包含「{}」的转发群！'.format(config.forward_groups)
    return None


def load_listen_sharing_groups(bot):
    """加载监控群"""
    if bot.is_listen_sharing:
        bot.listen_sharing_groups = search_groups(bot, config.listen_sharing_groups)
        if not len(bot.listen_sharing_groups):
            bot.listen_sharing_groups = []
            bot.is_listen_sharing = False
            return '未找到群名包含「{}」的分享监控群！'.format(config.listen_sharing_groups)
    return None


def load_timely_remind(bot):
    """定时提醒"""
    groups = search_groups(bot, config.timing_remind_groups)
    if not len(groups):
        bot.listen_sharing_groups = []
        bot.is_listen_sharing = False
        return '未找到群名包含「{}」的定时提醒群！'.format(config.listen_sharing_groups)
    weather_info = weather.get_timing(config.timing_location)
    for group in groups:
        group.send(weather_info)
    return None


def bot_status_detail(bot):
    """机器人配置状态"""
    bot_config_status = '机器人配置状态：'
    bot_config_status += '\n机器人管理员：{0}（{1}）'.format(bot.master.remark_name, bot.master.nick_name)

    bot_config_status += '\n好友自动回复：{}'.format(('是' if bot.is_friend_auto_reply else '否'))

    bot_config_status += '\n群聊回复：{}'.format(('是' if bot.is_group_reply else '否'))
    if bot.is_group_reply:
        bot_config_status += '，是否需要@才回复：{}'.format('是' if bot.is_group_at_reply else '否')

    bot_config_status += '\n是否开启防撤回模式：{}'.format(('是' if bot.is_forward_revoke_msg else '否'))

    bot_config_status += '\n是否开启监听模式：{}'.format('是' if bot.is_listen_friend else '否')
    if bot.is_listen_friend:
        bot_config_status += '，在{0}中监听{1}'.format(str(bot.listen_friend_groups), str(bot.listen_friends))

    bot_config_status += '\n是否开启转发模式：{}'.format(('是' if bot.is_forward_mode else '否'))
    if bot.is_forward_mode:
        bot_config_status += '\n转发模式已开启，您发送给我的任何信息都将被转发至:{}，您可发送命令：关闭转发模式 来关闭转发模式。'.format(
            str(bot.forward_groups))

    bot_config_status += '\n是否开启监控模式：{}'.format('是' if bot.is_listen_sharing else '否')
    if bot.is_listen_sharing:
        bot_config_status += '，将在以下群中监控分享：{}'.format(str(bot.listen_sharing_groups))
    return bot_config_status


def search_friend(bot, name):
    """查找某个好友
    优先级为：好友备注-好友昵称
    """
    nick_name_friend = None
    for friend in bot.friends():
        if getattr(friend, 'remark_name', None) == name:
            return friend
        elif not nick_name_friend and getattr(friend, 'nick_name', None) == name:
            nick_name_friend = friend
    return nick_name_friend or None


def search_friends(bot, names):
    """查找多个好友，用|分割
    匹配备注和微信昵称
    """
    split_names = names.split('|')
    result_list = []
    for friend in bot.friends():
        if getattr(friend, 'remark_name', None) in split_names:
            result_list.append(friend)
        elif getattr(friend, 'nick_name', None) in split_names:
            result_list.append(friend)
    return result_list


def search_groups(bot, groups):
    """查找多个群，用|分割
    """
    split_names = groups.split('|')
    result_list = []
    for group in split_names:
        try:
            result = bot.groups().search(group)
        except:
            print(group)
            print(bot.groups())
            print(bot.groups().search(group))
            result = []
        if len(result):
            result_list.extend(result)
    return result_list


