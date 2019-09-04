#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import urllib


def get(keyword):
    url = 'http://218.2.113.170:1159/music/play/' + urllib.parse.quote(keyword)
    return url


if __name__ == '__main__':
    result = get('五月天')
    print(result)
