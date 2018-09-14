# -*- encoding:utf-8 -*-

from utils.es_interface import es_client
from conf import settings
import datetime
import copy

if __name__ == "__main__":
    data = {
        'province': u'北京'.encode('utf-8'), 'country': 'china', 'county': '*'.encode('utf-8'),
        'server': '127.0.0.1', 'delay': 88, 'loss_rate': 0.1, 'time': 1502071380,
        'broadband': u'联通'.encode('utf-8'), 'counter': 29, 'app_id': '0987654321',
        'max_delay': 145, 'min_delay': 64, 'type': 'network',
    }
    delay_list = [
            25, 177, 194, 106, 46, 177, 89, 98, 48, 17,
            85, 59, 73, 171, 64, 200, 124, 197, 33, 141
            ]
    loss_list = [
            4.2, 4.6, 2.1, 2.2, 1.7, 0.8, 3.2, 2.6, 3.8, 2.0,
            0.6, 3.7, 3.2, 0.0, 4.3, 0.5, 4.1, 4.4, 2.5, 3.1
            ]
    province = [
            u'北京', u'上海', u'天津', u'重庆',
            u'黑龙江', u'吉林', u'辽宁', u'内蒙古', u'新疆', u'甘肃', u'宁夏', u'陕西', u'山西',
            u'河北', u'山东', u'河南', u'安徽', u'湖北', u'湖南', u'江苏', u'四川', u'西藏',
            u'云南', u'贵州', u'广西', u'广东', u'福建', u'浙江',
            ]
    carrier = [
            u'联通', u'移动', u'电信', u'其他'
            ]

    index = settings.opt['ELASTICSEARCH']['INDEX'].lower()
    es_client.create_index(index)
    for p in province:
        now = datetime.datetime.strptime('2017-08-07 09:52:00', "%Y-%m-%d %H:%M:%S")
        for i in xrange(len(loss_list)):
            now = now + datetime.timedelta(minutes=1)
            content = data.copy()
            content['province'] = p.encode('utf-8')
            content['loss_rate'] = loss_list[i]
            content['delay'] = delay_list[i]
            content['broadband'] = carrier[i%4].encode('utf-8')
            content['time'] = now.strftime("%Y-%m-%d %H:%M:%S")
            print es_client.create_record(index, content)

#     req_body = {
            # 'starttime': datetime.datetime.strptime('2017-08-07 09:53:00', "%Y-%m-%d %H:%M:%S"),
            # 'stoptime': datetime.datetime.strptime('2017-08-07 10:13:00', "%Y-%m-%d %H:%M:%S"),
            # # 'province': 'beijing',
            # # 'county': '*',
            # 'broadband': u'联通'.encode('utf-8'),
            # 'servers': ['127.0.0.1'],
            # # 'app_id': '0987654321',
            # 'datatype': 'delay',
            # }
#     print es_client.get_region_record(index, **req_body)
