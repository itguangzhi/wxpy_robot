#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import json

import requests

city_info = dict({'北京': {'id': 1100, 'name': 'beijing'},
                  '上海': {'id': 3100, 'name': 'shanghai'},
                  '广州': {'id': 4401, 'name': 'guangzhou'},
                  '深圳': {'id': 4403, 'name': 'shenzhen'},
                  '武汉': {'id': 4201, 'name': 'wuhan'},
                  '天津': {'id': 1200, 'name': 'tianjin'},
                  '南京': {'id': 3201, 'name': 'nanjing'},
                  '香港': {'id': 8100, 'name': 'xianggang'},

                  '重庆': {'id': 5000, 'name': 'chongqing'},
                  '杭州': {'id': 3301, 'name': 'hangzhou'},
                  '沈阳': {'id': 2101, 'name': 'shenyang'},
                  '大连': {'id': 2102, 'name': 'dalian'},
                  '成都': {'id': 5101, 'name': 'chengdu'},
                  '长春': {'id': 2201, 'name': 'changchun'},
                  '苏州': {'id': 3205, 'name': 'suzhou'},
                  '佛山': {'id': 4406, 'name': 'foshan'},
                  '昆明': {'id': 5301, 'name': 'kunming'},
                  '西安': {'id': 6101, 'name': 'xian'},
                  '郑州': {'id': 4101, 'name': 'zhengzhou'},
                  '长沙': {'id': 4301, 'name': 'changsha'},
                  '宁波': {'id': 3302, 'name': 'ningbo'},
                  '无锡': {'id': 3202, 'name': 'wuxi'},
                  '青岛': {'id': 3702, 'name': 'qingdao'},
                  '南昌': {'id': 3601, 'name': 'nanchang'},
                  '福州': {'id': 3501, 'name': 'fuzhou'},
                  '东莞': {'id': 4419, 'name': 'dongguan'},
                  '南宁': {'id': 4501, 'name': 'nanning'},
                  '合肥': {'id': 3401, 'name': 'hefei'},
                  '贵阳': {'id': 5201, 'name': 'guiyang'},
                  '厦门': {'id': 3502, 'name': 'xiamen'},
                  '哈尔滨': {'id': 2301, 'name': 'haerbin'},
                  '石家庄': {'id': 1301, 'name': 'shijiazhuang'},
                  })


def request_get(url, params):
    response = requests.get(url=url, params=params)
    result = json.loads(response.text, encoding='utf8')
    return result


def get_st_transfers(st_r, ls, r_base):
    """获取换乘站"""
    st = st_r.split('|')
    st.remove(ls)
    res = [r_base.get(i, '') for i in st] if len(st) > 0 else list()
    return ','.join(res)


def get_route_name(routes, route_name):
    """获取地铁线路名称"""

    if len(route_name) == 0:
        return route_name
    route_name = route_name.upper()
    a = [a for a in routes if a.startswith(route_name)]
    if len(a) >= 1:
        return a[0]

    a = [a for a in routes if route_name in a]
    return a[0] if len(a) >= 1 else route_name


def get_route(code, name, route_name):
    """获取地铁详情"""
    url = 'http://map.amap.com/service/subway'
    params = {'srhdata': '{0}_drw_{1}.json'.format(code, name)}
    route_info = request_get(url, params)
    route_info_base = dict(zip([route['ls'] for route in route_info['l']], [route['ln'] for route in route_info['l']]))
    route_name = get_route_name(list(route_info_base.values()), route_name)
    result = [{'r_name': route['ln'],
               'r_code': route['ls'],
               'r_enable': '' if route['su'] == '1' else '建设中',
               'r_stations': [{'st_code': st['si'],
                               'st_name': st['n'],
                               'st_route': get_st_transfers(st['r'], route['ls'], route_info_base),
                               'st_is_transfers': '可换乘' if st['t'] == '1' else '',
                               'st_enable': '' if st['su'] == '1' else '建设中'}
                              for st in route['st']]}
              for route in route_info['l'] if route['ln'] == route_name]
    return route_info_base, result, route_name


def get_station_time(code, name, route_code):
    """获取站台时刻信息"""
    url = 'http://map.amap.com/service/subway'
    params = {'srhdata': '{0}_info_{1}.json'.format(code, name)}
    station_time_info = request_get(url, params)
    result = [{st['si']: {d['n']: {'latest': d['lt'], 'earliest': d['ft']} for d in st['d']} for st in route['st']}
              for route in station_time_info['l'] if route['ls'] == route_code]
    return result[0]


def get(city_name, route_name):
    city = city_info.get(city_name)
    if city is None:
        return '未查到{} {}地铁'.format(city_name, route_name)

    routes, route_infos, route_name = get_route(city['id'], city['name'], route_name)
    if len(route_name) == 0:
        routes_names = list(routes.values())
        routes_names.insert(0, '{}地铁线：'.format(city_name))
        return '\r\n'.join(routes_names)
    if len(route_infos) == 0:
        return '未查到{} {}地铁'.format(city_name, route_name)

    route_info = route_infos[0]
    route_info['r_stations'].reverse()
    station_time_info = get_station_time(city['id'], city['name'], route_info['r_code'])
    first_st_code, last_st_code = route_info['r_stations'][0]['st_code'], route_info['r_stations'][-1]['st_code']
    first_st_name, last_st_name = route_info['r_stations'][0]['st_name'], route_info['r_stations'][-1]['st_name']

    content_list = list()
    content_list.append('{} {} 站台时刻表: {}'.format(city_name, route_info['r_name'], route_info['r_enable']))
    content_list.append("-----------------------------")
    r_stations = route_info['r_stations']
    for route in r_stations:
        st = station_time_info[route['st_code']]
        st_route = '\r\n  可换乘:\r\n    {}'.format(route['st_route']) if len(route['st_route']) > 0 else ''
        content = '{0}:\r\n  往{1}方向:\r\n    首班{2},末班{3}\r\n  往{4}方向:\r\n    首班{5},末班{6}{7}'.format(
            route['st_name'],
            first_st_name,
            st[first_st_code]['earliest'],
            st[first_st_code]['latest'],
            last_st_name,
            st[last_st_code]['earliest'],
            st[last_st_code]['latest'],
            st_route,
        )
        content_list.append(content)
        content_list.append("-----------------------------")
    return '\r\n'.join(content_list)


if __name__ == '__main__':
    result = get('南京', '1')
