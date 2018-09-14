# -*- encoding:utf-8 -*-

from utils.es_userquery import es_trace
from conf import settings
import datetime
import copy

if __name__ == "__main__":
    data = {'timestamp': 1502071380,
        'app_id': '0987654321',
        'remote_ip': '127.0.0.1', 
        'user_id': '0987654321',
        'user_name': 'littlegirl',
        'channel': 'ios app store',
        'server_id': '0987654321',
        'target_ip': '127.0.0.1',
        'device_id': '0987654321',
        'device_name': '0987654321',
        'device_version': '0987654321',
        'device_type': '0987654321',
        'location': u'北京'.encode('utf-8'),
        'log_type': 'trace',
        'net_type': 'WIFI',
        'net_delay': 40,
        'wifi_count': 12,
        'wifi_rssi': 12,
        'wifi_channel': 12,
        'frequency': 1200,
        'speed': 120,
        'rount_delay': 10.0,
        'local_delay': 10.0,
        'cell_rssi': 12,
        'cell_delay': 120.0
    }
    delay_list = [
            25, 177, 194, 106, 46, 177, 89, 98, 48, 17,
            85, 59, 73, 171, 64, 200, 124, 197, 33, 141,
            25, 177, 194, 106, 46, 177, 89, 98, 48, 17,
            85, 59, 73, 171, 64, 200, 124, 197, 33, 141
            ]
    rount_list = [
            4.2, 4.6, 2.1, 2.2, 1.7, 0.8, 3.2, 2.6, 3.8, 2.0,
            0.6, 3.7, 3.2, 0.0, 4.3, 0.5, 4.1, 4.4, 2.5, 3.1,
            4.2, 4.6, 2.1, 2.2, 1.7, 0.8, 3.2, 2.6, 3.8, 2.0,
            0.6, 3.7, 3.2, 0.0, 4.3, 0.5, 4.1, 4.4, 2.5, 3.1,
            ]
    index = settings.opt['ELASTICSEARCH']['TRACEINDEX'].lower()
    es_trace.create_index(index)
    now = datetime.datetime.strptime('2017-08-28 09:52:00', "%Y-%m-%d %H:%M:%S")
    for i in xrange(len(delay_list)):
        now = now + datetime.timedelta(minutes=20)
        content = data.copy()
        content['device_id'] = '2222222222'
        content['user_id'] = '2222222222'
        content['net_delay'] = delay_list[i]
        content['rount_delay'] = rount_list[i]
        content['timestamp'] = now.strftime("%Y-%m-%d %H:%M:%S")
        print es_trace.create_record(index, content)

    req_body = {
            'device_id': '2222222222',
            'target_ip': '127.0.0.1',
            'appid': '0987654321',
            'userid': '2222222222',
            'starttime': datetime.datetime.strptime('2017-08-28 09:52:00', "%Y-%m-%d %H:%M:%S"),
            'stoptime': datetime.datetime.strptime('2017-08-29 11:52:00', "%Y-%m-%d %H:%M:%S"),
            }
    print es_trace.get_record(index, **req_body)
