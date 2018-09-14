# -*- encoding:utf-8 -*-

from utils.es_userquery import es_heart
from conf import settings
import datetime
import copy

if __name__ == "__main__":
    interval = 100
    data = {
        'app_id': '0987654321',
        'remote_ip': '127.0.0.1', 
        'device_id': '0987654321',
        'target_ip': '127.0.0.1', 
        'net_type': 'WIFI',
        'log_type': 'heart_beat',
        'timestamp': 1502071380,
        'min_delay': '0',
        'max_delay': '500',
        'mid_delay': '250',
        'avg_delay': '200',
        'lost_rate': '0.1',
        'interval': interval,
        'delay_list': [11, 22],
    }
    delay_list = [
            25, 177, 194, 106, 46, 177, 89, 98, 48, 17,
            85, 59, 73, 171, 64, 200, 124, 197, 33, 141,
            25, 177, 194, 106, 46, 177, 89, 98, 48, 17,
            85, 59, 73, 171, 64, 200, 124, 197, 33, 141
            ]
    loss_list = [
            4.2, 4.6, 2.1, 2.2, 1.7, 0.8, 3.2, 2.6, 3.8, 2.0,
            0.6, 3.7, 3.2, 0.0, 4.3, 0.5, 4.1, 4.4, 2.5, 3.1,
            4.2, 4.6, 2.1, 2.2, 1.7, 0.8, 3.2, 2.6, 3.8, 2.0,
            0.6, 3.7, 3.2, 0.0, 4.3, 0.5, 4.1, 4.4, 2.5, 3.1,
            ]
    deviceid_list = [
            '1111111111', '2222222222', '3333333333', '4444444444'
            ]
    index = settings.opt['ELASTICSEARCH']['HEARTINDEX'].lower()
    es_heart.create_index(index)
    now = datetime.datetime.strptime('2017-08-28 02:19:00', "%Y-%m-%d %H:%M:%S")
    for i in xrange(len(delay_list)):
        now = now + datetime.timedelta(minutes=1)
        content = data.copy()
        content['device_id'] = deviceid_list[1]
        content['lost_rate'] = loss_list[i]
        content['avg_delay'] = delay_list[i]
        content['delay_list'] = [delay_list[i] for j in range(60 * 1000 / interval)]
        content['timestamp'] = now.strftime("%Y-%m-%d %H:%M:%S")
        print es_heart.create_record(index, content)
    req_body = {
            'appid': '0987654321',
            'device_id': deviceid_list[1],
            'target_ip': '127.0.0.1',
            'starttime': datetime.datetime.strptime('2017-08-28 02:19:00', "%Y-%m-%d %H:%M:%S"),
            'duration': 1020,
            }
    print es_heart.get_record(index, **req_body)
