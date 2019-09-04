#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import requests
import json

lbs_key = '81ab2641c0c4dd947318b37125ba231d'
lbs_output = 'json'


def request_get(url, params):
    response = requests.get(url=url, params=params)
    result = json.loads(response.text, encoding='utf8')
    return result


def get_direction_driving(origin, destination):
    url = 'https://restapi.amap.com/v3/direction/driving'
    params = dict()
    params['key'] = lbs_key
    params['output'] = lbs_output
    params['origin'] = origin
    params['destination'] = destination
    params['extensions'] = 'all'
    params['strategy'] = 10

    response = request_get(url=url, params=params)
    return response


def get_geocode_geo(address):
    url = 'https://restapi.amap.com/v3/geocode/geo'
    params = dict()
    params['key'] = lbs_key
    params['output'] = lbs_output
    params['batch'] = True
    params['address'] = address
    params['city'] = ''

    response = request_get(url=url, params=params)
    geocodes = response.get('geocodes', list())
    address_info = list()
    for geocode in geocodes:
        item = dict()
        item['formatted_address'] = geocode.get('formatted_address')
        item['adcode'] = geocode.get('adcode')
        item['location'] = geocode.get('location')
        address_info.append(item)
    return address_info


def get_route(address):
    address_info = get_geocode_geo(address)
    origin = address_info[0]['location']
    destination = address_info[1]['location']
    dirve_info = get_direction_driving(origin, destination)
    return dirve_info


if __name__ == '__main__':
    result = get_route('总统府|宁国市吴越古道细哥农家乐')
    str_res = json.dumps(result, indent=4, ensure_ascii=False)
    print(str_res)
