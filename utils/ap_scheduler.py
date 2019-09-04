#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import time
from apscheduler.schedulers.background import BackgroundScheduler


def _test():
    print('Test !!!')


def timely_execute(function, hour, minute, args):
    """定时每天hour点minute分执行方法"""

    # BackgroundScheduler: 适合于要求任何在程序后台运行的情况，当希望调度器在应用后台执行时使用。
    scheduler = BackgroundScheduler()
    # 采用非阻塞的方式，间隔3秒钟执行一次
    scheduler.add_job(function, 'cron', day_of_week='*', hour=hour, minute=minute, second='0', args=args)
    # 这是一个独立的线程
    scheduler.start()


if __name__ == '__main__':
    timely_execute(_test, 22, 31, [])
    # while True:
    #     print('main-start:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    #     time.sleep(3)
    #     print('main-end:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
