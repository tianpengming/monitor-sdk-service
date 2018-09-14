# -*- encoding:utf-8 -*-

from tornado.web import RequestHandler
from werkzeug.datastructures import ImmutableMultiDict
import datetime

from model.userquery_form import (
    MonitorUserQuerySearchForm, MonitorUserQueryDetailForm,
    MonitorHeartbeatForm,
    MonitorTraceForm, MonitorTraceDetailForm, TraceAllForm,
)

from utils.exceptions import Status400, Status403, except_handler
from utils.es_userquery import es_query, es_trace, es_heart, es_account
from utils.get_ip import get_ipaddr, get_ipaddr_info, get_ipaddr_list
from conf import settings


import logging
logger = logging.getLogger()

class MonitorUserQueryHandler(RequestHandler):

    @except_handler()
    def get(self, req_data):
        form = MonitorUserQuerySearchForm(ImmutableMultiDict(req_data))
        if not form.validate():
            raise Status400(form.errors)
        search_data = {k: v for k, v in form.data.iteritems() if v!=u''}
        get_data = es_account.get_record(
            settings.opt['ELASTICSEARCH']['ACCOUNTINDEX'],
            **search_data
        )
        get_data.update({'result': 0, 'message': 'success'})
        return get_data

class MonitorUserQueryDetailHandler(RequestHandler):

    #     def initialize(self):
    # self.db_session = Session()

    # def on_finish(self):
    # self.db_session.close()

    @except_handler()
    def get(self, req_data):
        form = MonitorUserQueryDetailForm(ImmutableMultiDict(req_data))
        if not form.validate():
            raise Status400(form.errors)
        get_data = es_query.get_detail_record(
            settings.opt['ELASTICSEARCH']['QUERYINDEX'],
            **form.data
        )
        #         region_name = 'unknown'
        # if get_data:
        # server_inst = self.db_session.query(MonitorServerIp).filter(
        # MonitorServerIp.ip==get_data['target_ip']).first()
        # if server_inst:
        #                 region_name = server_inst._region.name
        get_data.update({'result': 0, 'message': 'success'})
        return get_data


class MonitorHeartbeatHandler(RequestHandler):

    @staticmethod
    def pos_from_time(pos_time, start_time, interval):
        delta = pos_time - start_time
        pos = delta.total_seconds() * 1000 / interval
        return pos

    @except_handler()
    def get(self, req_data):
        form = MonitorHeartbeatForm(ImmutableMultiDict(req_data))
        if not form.validate():
            raise Status400(form.errors)
        get_data = es_heart.get_record(
            settings.opt['ELASTICSEARCH']['HEARTINDEX'],
            **form.data
        )
        if len(get_data['dlist'])==0:
            return {'result': 0,
                    'message': 'success',
                    'interval': 0,
                    'instance': [],
                    'trace_list': [],
                    }
        # 检查时间断点
        sorted_data = sorted(get_data['dlist'], cmp=lambda x,y: cmp(x['time'], y['time']))
        mseconds = form.data['duration'] * 1000
        ret_data = []
        s_flag, count_flag = 0, 0.0
        interval = get_data['interval']
        sorted_len = len(sorted_data)
        last_flag = False
        while count_flag <= mseconds:
            now = form.data['starttime'] + datetime.timedelta(seconds=count_flag/1000)
            s_flag_time = sorted_data[s_flag]['time']
            delay_len = len(sorted_data[s_flag]['delay_list'])
            delta = sorted_data[s_flag]['interval'] * delay_len / 100
            time_flag = datetime.datetime.strptime(s_flag_time,'%Y-%m-%d %H:%M:%S')-datetime.timedelta(seconds=delta*0.1)
            # logger.debug('xxxxxxxxxxxxxxxxxxxxxxxxxxx')
            # logger.debug('{0} --- {1} --- {2}'format(s_flag_time, sorted_data[s_flag]['interval'], delay_len))
            # logger.debug('{0} --- {1}'.format(now, time_flag))
            # logger.debug('{0} --- {1} --- {2}'.format(count_flag, mseconds, len(ret_data)))
            # logger.debug('xxxxxxxxxxxxxxxxxxxxxxxxxxx')
            if time_flag < now:
                if s_flag == sorted_len - 1 and last_flag is True:
                    ret_data.append({'loss_rate': '-', 'delay': '-',})
                    count_flag = count_flag + interval
                else:
                    tmp_time = datetime.datetime.strptime(s_flag_time,'%Y-%m-%d %H:%M:%S')-now
                    tmp_len = tmp_time.seconds * 1000 / sorted_data[s_flag]['interval']
                    for j in range(tmp_len):
                        if sorted_data[s_flag]['delay_list'][j] == 0:
                            sorted_data[s_flag]['delay_list'][j] = get_data['delay_top']
                        ret_data.append(
                            {'loss_rate': sorted_data[s_flag]['loss_rate'],
                             'delay': sorted_data[s_flag]['delay_list'][j]}
                        )
                        for jj in range((sorted_data[s_flag]['interval']-interval)/interval):
                            ret_data.append({'loss_rate': '-', 'delay': '-',})
                    s_flag = s_flag + 1
                    if s_flag == sorted_len:
                        last_flag = True
                        s_flag = s_flag - 1
                    count_flag = count_flag + tmp_len * sorted_data[s_flag]['interval']
            elif time_flag == now:
                for j in sorted_data[s_flag]['delay_list']:
                    if j == 0:
                        j = get_data['delay_top']
                    ret_data.append(
                        {'loss_rate': sorted_data[s_flag]['loss_rate'],
                         'delay': j}
                    )
                    for jj in range((sorted_data[s_flag]['interval']-interval)/interval):
                        ret_data.append({'loss_rate': '-', 'delay': '-',})
                s_flag = s_flag + 1
                if s_flag == sorted_len:
                    last_flag = True
                    s_flag = s_flag - 1
                count_flag = count_flag + delta * 100
            else:
                ret_data.append({'loss_rate': '-', 'delay': '-',})
                count_flag = count_flag + interval
        # 新增主动检测匹配功能
        start_time = form.data['starttime']
        stop_time = start_time + datetime.timedelta(seconds=form.data['duration'])
        trace_time = es_trace.get_record(
            settings.opt['ELASTICSEARCH']['TRACEINDEX'],
            userid = form.data['user_id'],
            appid = form.data['appid'],
            starttime = start_time,
            stoptime = stop_time,
        )
        trace_list = [
            {'pos': MonitorHeartbeatHandler.pos_from_time(
                datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S'),
                start_time,
                interval),
                'timestamp': t}
            for t in trace_time['checktimes']
            ]
        return {'result': 0,
                'message': 'success',
                'interval': interval,
                'instance': ret_data,
                'trace_list': trace_list,
                }

class MonitorTraceHandler(RequestHandler):

    @except_handler()
    def get(self, req_data):
        form = MonitorTraceForm(ImmutableMultiDict(req_data))
        if not form.validate():
            raise Status400(form.errors)
        get_data = es_trace.get_record(
            settings.opt['ELASTICSEARCH']['TRACEINDEX'],
            **form.data
        )
        get_data.update({'result': 0, 'message': 'success'})
        return get_data

class MonitorTraceDetailHandler(RequestHandler):

    delay_check_list = ['route_delay', 'local_delay', 'cell_delay']

    def initialize(self):
        self.max_delay = 999

    @classmethod
    def check_ipv4(cls, value):
        parts = value.split('.')
        if len(parts) == 4 and all(x.isdigit() for x in parts):
            numbers = list(int(x) for x in parts)
            return all(num >= 0 and num < 256 for num in numbers)
        return False

    @except_handler()
    def get(self, req_data):
        form = MonitorTraceDetailForm(ImmutableMultiDict(req_data))
        if not form.validate():
            raise Status400(form.errors)
        get_data = es_trace.get_detail_record(
            settings.opt['ELASTICSEARCH']['TRACEINDEX'],
            **form.data
        )
        max_delay = get_data['instance'].get('delay_top', self.max_delay)
        for item in get_data['instance']['traceroute']:
            if item['ip'] == '***':
                item['county'] = u'未知'.encode('utf-8')
                item['broadband'] = u'未知'.encode('utf-8')
                item['delay'] = round(item['delay'], 2)
            elif MonitorTraceDetailHandler.check_ipv4(item['ip']):
                ip_info = get_ipaddr_info(item['ip'])
                item['county'] = ip_info['county']
                item['broadband'] = ip_info['broadband']
                item['delay'] = round(item['delay'], 2)
            else:
                item['ip'] = '***'
                item['county'] = u'未知'.encode('utf-8')
                item['broadband'] = u'未知'.encode('utf-8')
                item['delay'] = max_delay
            if item['delay'] == 0 or item['delay'] > max_delay:
                item['delay'] = max_delay
        for item in MonitorTraceDetailHandler.delay_check_list:
            if get_data['instance'].get(item, 0.0) == 0.0:
                get_data['instance'][item] = max_delay
        get_data.update({'result': 0, 'message': 'success'})
        return get_data

class TraceAllHandler(RequestHandler):

    @except_handler()
    def get(self, req_data):
        form = TraceAllForm(ImmutableMultiDict(req_data))
        if not form.validate():
            raise Status400(form.errors)
        get_data = es_trace.get_all_record(
            settings.opt['ELASTICSEARCH']['TRACEINDEX'],
            **form.data
        )
        ip_dict = {}
        ip_list = []
        for item in get_data:
            for data in item['traceroute']:
                find_delay = lambda x, y: y if x==0.0 else x
                if MonitorTraceDetailHandler.check_ipv4(data['ip']):
                    if data['ip'] not in ip_list:
                        ip_dict[data['ip']] = {'delay': find_delay(data['delay'], item['delay_top']),
                                               'counter': 1}
                        ip_list.append(data['ip'])
                    else:
                        ip_dict[data['ip']]['delay'] = ip_dict[data['ip']]['delay'] + \
                                                       find_delay(data['delay'], item['delay_top'])
                        ip_dict[data['ip']]['counter'] = ip_dict[data['ip']]['counter'] + 1
        ip_ret = get_ipaddr_list(ip_list)
        instance = [
            {
                'ip': k,
                'delay': v['delay'] / v['counter'],
                'broadband': ip_ret[k]['broadband'],
                'country': ip_ret[k]['country'],
                'county': ip_ret[k]['county'],
            }
            for k, v in ip_dict.iteritems()
            if ip_ret[k]['country'] != '局域网'.encode() and ip_ret[k]['county'] != '局域网'.encode()
            ]
        ret = {'result':0, 'message': 'success', 'instance': instance}
        return ret