# -*- encoding:utf-8 -*-

from utils.es_userquery import es_query
from conf import settings
import datetime
import copy

if __name__ == "__main__":
    data = {
        'app_id': '0987654321',
        'remote_ip': '127.0.0.1', 
        'log_type': 'user_query',
        'game_num': '0987654321',
        'user_id': '0987654321',
        'user_name': 'littlegirl',
        'start_time': 1502071380,
        'dur_time': '3360',
        'server_name': 'fenghuoliantian',
        'target_ip': '127.0.0.1', 
        'device_id': '0987654321',
    }
    durtime_list = [
            25, 177, 194, 106, 46, 177, 89, 98, 48, 17,
            85, 59, 73, 171, 64, 200, 124, 197, 33, 141,
            85, 177, 73, 106, 64, 46, 98, 197, 48, 141,
            25, 177, 90, 106, 46, 177, 89, 17, 85, 71,
            ]
    deviceid_list = ['1111111111', '2222222222', '3333333333', '4444444444']
    username_list = ['biggirl', 'threebody', '1123234', 'sdfsdfu']
    userid_list = ['1111111111', '2222222222', '3333333333', '4444444444']
    index = settings.opt['ELASTICSEARCH']['QUERYINDEX'].lower()
    es_query.create_index(index)
    now = datetime.datetime.strptime('2017-08-27 09:52:00', "%Y-%m-%d %H:%M:%S")
    game_num_base = 10000000
#     for i in xrange(len(durtime_list)):
        # now = now + datetime.timedelta(minutes=durtime_list[i]+1)
        # content = data.copy()
        # content['device_id'] = deviceid_list[i%4]
        # content['user_id'] = userid_list[i%4]
        # content['user_name'] = username_list[i%4]
        # content['dur_time'] = durtime_list[i] * 60
        # content['game_num'] = '{}'.format(game_num_base + i)
        # content['start_time'] = now.strftime("%Y-%m-%d %H:%M:%S")
#         print es_query.create_record(index, content)

    req_body = {
            'startpos': 0,
            'length': 20,
            }
    print es_query.get_record(index, **req_body)
