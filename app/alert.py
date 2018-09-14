# -*- encoding:utf-8 -*-

from __future__ import absolute_import

from tornado.web import RequestHandler
from werkzeug.datastructures import ImmutableMultiDict
from sqlalchemy import or_
import datetime

from model.region import MonitorRegion, MonitorServerIp
from model.common import Session
from model.alert import (
        MonitorAlertLog, MonitorAlertLogGetForm, MonitorAlertDashGetForm,
        MonitorAlertDashDetailForm,
        )
from model.rule import MonitorTrigger, MonitorRule
from utils.exceptions import Status400, Status403, except_handler
from utils.serializer import AlchemyEncoder
from utils.es_interface import es_client
from utils.redis_cache import RedisCache
from utils.emit_mail import send_mail
from conf import settings

import logging
logger = logging.getLogger()

PeriodInt = {'1min': 1, '5min': 5, '10min': 10, '30min': 30, '1h': 60}
TimeInt = {'1c': 1, '2c': 2, '3c': 3, '4c': 4, '5c': 5, '6c': 6, '7c': 7, '8c': 8, '9c': 9, '10c': 10}
RepeatInt = {'5min':5, '10min':10, '15min':15, '30min':30,
        '1h':60, '2h':120, '3h':180, '5h':300,'12h':720}
CarrierList = [u'联通'.encode('utf-8'), u'移动'.encode('utf-8'), u'电信'.encode('utf-8')]

class MonitorAlertLogHandler(RequestHandler):

    def initialize(self):
        self.db_session = Session()

    def on_finish(self):
        self.db_session.close()

    @except_handler()
    def get(self, req_data):
        form = MonitorAlertLogGetForm(ImmutableMultiDict(req_data))
        if not form.validate():
            raise Status400(form.errors)
        if form.data['state'] == 'all':
            data_list = self.db_session.query(MonitorAlertLog).filter(
                    MonitorAlertLog.start_time>form.data['starttime'],
                    MonitorAlertLog.start_time<form.data['stoptime'],
                    ).all()
        else:
            data_list = self.db_session.query(MonitorAlertLog).filter(
                    MonitorAlertLog.start_time>form.data['starttime'],
                    MonitorAlertLog.start_time<form.data['stoptime'],
                    MonitorAlertLog.state==form.data['state'],
                    ).all()
        serialized = []
        for item in data_list:
            rec = {
                'uuid': item.id,
                'state': item.state,
                'starttime': item.start_time,
                'content': item.content,
                'region': item.region,
                'dest': u'{0}{1}'.format(item.province, item.county),
            }
            start_time = datetime.datetime.strptime(item.start_time, '%Y-%m-%d %H:%M:%S')
            stop_time = datetime.datetime.strptime(item.stop_time, '%Y-%m-%d %H:%M:%S')
            if item.state=='close':
                if stop_time > start_time:
                    rec['duration'] = (stop_time - start_time).seconds / 60
                else:
                    rec['duration'] = (start_time - stop_time).seconds / 60
            else:
                rec['duration'] = (datetime.datetime.now() - start_time).seconds / 60
            serialized.append(rec)
        return {'instance': serialized, 'result': 0, 'message': 'success'}

#     @except_handler()
    # def delete(self, req_data):
        # if not req_data.has_key('id'):
            # raise Status400('id is required')
        # result = MonitorAlertLog._validate(self.db_session, req_data['id'])
        # instance = result['instance']
        # if instance is None:
            # raise Status403(result['message'])
        # instance._delete(self.db_session)
        # return {'id': '{}'.format(instance.id),
                # 'result': 0, 'message': 'success',
#                 }

class MonitorAlertLogDetailHandler(RequestHandler):

    def initialize(self):
        self.db_session = Session()

    def on_finish(self):
        self.db_session.close()

    @except_handler()
    def get(self, req_data):
        if not req_data.has_key('id'):
            raise Status400('id is required')
        instance = self.db_session.query(MonitorAlertLog).get(req_data['id'][0])
        if not instance:
            raise Status403('alert log id is invalid')
        origin_data = AlchemyEncoder().parse_sqlalchemy_object(instance)
        key_list = ['start_time', 'region', 'state', 'content_detail', 'rule_name', 'broadband', 'id']
        ret_data = {key: value for key, value in origin_data.iteritems() if key in key_list}
        if origin_data['state'] == 'close':
            stop_time = datetime.datetime.strptime(origin_data['stop_time'], '%Y-%m-%d %H:%M:%S')
            start_time = datetime.datetime.strptime(origin_data['start_time'], '%Y-%m-%d %H:%M:%S')
            if stop_time < start_time:
                time_delta = start_time - stop_time
            else:
                time_delta = stop_time - start_time
            ret_data['duration'] = time_delta.seconds / 60
        else:
            now = datetime.datetime.now()
            start_time = datetime.datetime.strptime(origin_data['start_time'], '%Y-%m-%d %H:%M:%S')
            time_delta = now - start_time
            ret_data['duration'] = time_delta.seconds / 60
        if origin_data['county'] == '*':
            ret_data['county'] = origin_data['province']
        else:
            ret_data['county'] = '{0}{1}'.format(origin_data['province'], origin_data['county'])
        return {
            'result': 0, 'message': 'success',
            'instance': ret_data,
        }


class MonitorAlertConfirmHandler(RequestHandler):

    def initialize(self):
        self.db_session = Session()
        self.redis = RedisCache()

    def on_finish(self):
        self.db_session.close()

    '''
    trig_id: MonitorTrigger id
    '''
    def make_confirm(self, trig_id, ip, province, county, broadband, appid, state):
        flag = 'cfm:{0};{1};{2};{3};{4};{5}'.format(trig_id, ip, province, county, broadband, appid)
        if state=='confirm':
            ret = self.redis.set_data(flag, True)
        if state=='cansel':
            ret = self.redis.del_data(flag) 
        if not ret:
            return False
        return True

    @except_handler()
    def post(self, req_data):
        if not req_data.has_key('id'):
            raise Status400('id is required')
        instance = self.db_session.query(MonitorAlertLog).get(req_data['id'][0])
        if not instance:
            raise Status400('id not exists')
        if instance.state != 'open':
            raise Status400('state is not open')
        ret = self.make_confirm(
                instance.trigger, instance.serverip, instance.province,
                instance.county, instance.broadband, instance.appid, 'confirm'
                )
        if not ret:
            return {'result': -1, 'message': 'success', 'id': req_data['id']}
        instance.state = 'confirm'
        instance.content_detail  = u'{}<br/>告警已经确认。'.format(instance.content_detail).encode('utf8')
        instance._save(self.db_session, update=True)
        return {'result': 0, 'message': 'success', 'id': req_data['id']}

class MonitorAlertDashDetailHandler(RequestHandler):

    def initialize(self):
        self.db_session = Session()

    def on_finish(self):
        self.db_session.close()

    @except_handler()
    def get(self, req_data):
        form = MonitorAlertDashDetailForm(ImmutableMultiDict(req_data))
        if not form.validate():
            raise Status400(form.errors)
        form_data = form.data.copy()
        region = form_data.pop('region')
        ser_instance = self.db_session.query(MonitorRegion).get(region)
        if not ser_instance:
            raise Status403('region id is invalid')
        server_list = [i.ip for i in ser_instance._serverips]
        # logger.debug('{0}'.format(form_data))
        form_data['broadband'] = form_data['broadband'].split(',')
        origin_data = es_client.get_province_record(
                settings.opt['ELASTICSEARCH']['INDEX'],
                servers=server_list, **form_data 
                )
        # logger.debug('{0}'.format(origin_data))
        ip_total = 0
        avg_delay, avg_loss = 0, 0
        for item in origin_data['county_net']:
            ip_total = ip_total + item['counter']
        for item in origin_data['county_net']:
            avg_delay = avg_delay + item['delay'] * item['counter'] / ip_total
            avg_loss = avg_loss + item['loss_rate'] * item['counter'] / ip_total
            item['ip_perc'] = item['counter'] / ip_total * 100
        return {'return': 0, 'message': 'success', 'ip_total': ip_total,
                'avg_delay': avg_delay, 'avg_loss': avg_loss, 
                'update_time': origin_data['updatetime'],
                'instance': origin_data['county_net']
                }

'''
Get alert input and Emit alert
'''
class MonitorAlertHandler(RequestHandler):

    def initialize(self):
        self.db_session = Session()
        self.redis = RedisCache()

    def on_finish(self):
        self.db_session.close()

    @except_handler()
    def get(self, req_data):
        form = MonitorAlertDashGetForm(ImmutableMultiDict(req_data))
        if not form.validate():
            raise Status400(form.errors)
        form_data = form.data.copy()
        region = form_data.pop('region')
        ser_instance = self.db_session.query(MonitorRegion).get(region)
        if not ser_instance:
            raise Status403('region id is invalid')
        server_list = [i.ip for i in ser_instance._serverips]
        form_data['broadband'] = form_data['broadband'].split(',')
        origin_data = es_client.get_region_record(
                settings.opt['ELASTICSEARCH']['INDEX'],
                servers=server_list, **form_data 
                )
        for item in origin_data:
            if form_data['datatype']=='delay':
                item['level'] = MonitorAlertHandler.set_level(
                    form_data['datatype'], delay=item['delay'])
            elif form_data['datatype']=='loss_rate':
                item['level'] = MonitorAlertHandler.set_level(
                    form_data['datatype'], loss_rate=item['loss_rate'])
            else:
                item['level'] = MonitorAlertHandler.set_level(
                    form_data['datatype'], item['delay'], item['loss_rate'])
        return {'return': 0, 'message': 'success',
                'instance': origin_data}

    @staticmethod
    def set_level(datatype, delay=0, loss_rate=0):
        loss_level, delay_level = 0, 0
        if datatype=='loss_rate' or datatype=='all':
            if loss_rate >= 0 and loss_rate <= 0.5:
                loss_level = 0 
            elif loss_rate >= 0.6 and loss_rate <= 1.0:
                loss_level = 1
            elif loss_rate >= 1.1 and loss_rate <= 2.0:
                loss_level = 2
            elif loss_rate >= 2.1 and loss_rate <= 5.0:
                loss_level = 3
            else:
                loss_level = 4
        if datatype=='delay' or datatype=='all':
            if delay >= 0 and delay <= 50:
                delay_level = 0
            elif delay > 50 and delay <= 100:
                delay_level = 1
            elif delay > 100 and delay <= 150:
                delay_level = 2
            elif delay > 150 and delay <= 200:
                delay_level = 3
            else:
                delay_level = 4
        if datatype=='loss_rate':
            return loss_level 
        elif datatype=='delay':
            return delay_level
        else:
            return delay_level if delay_level > loss_level else loss_level

    '''
    serialize original data
    input: [
        "_id": xxxxxx,
        "_source": {
            "datetime": '2017-08-01 12:12:00'
            "province": 'beijing'
            "county": '*' 
            "server": '192.168.152.22'
            "data": '{
                'province': 'beijing', 'country': 'china', 'county': '*',
                'server': '10.40.44.2', 'delay': 88, 'loss_rate': 92, 'time': 1502071380,
                'broadband': 'xxx', 'counter': 29, 'app_id': '0987654321',
                'max_delay': 145, 'min_delay': 64, 'type': 'network', 'devices': 1,
                }'
            }
        ...
        ]
    trigger和severip联合识别，一个报警对应于一个trigger，一个serverip组成的共同记录
    '''
    def alert_handler(self, req_data):
        alert_result = []
        # province = req_data['province']
        # county = req_data['county']
        serverip = self.db_session.query(MonitorServerIp).filter(MonitorServerIp.ip==req_data['server']).first()
        if not serverip:
            return alert_result
        region = self.db_session.query(MonitorRegion).filter(MonitorRegion._serverips.contains(serverip)).first()
        if not region:
            return alert_result
        rules = self.db_session.query(MonitorRule).filter(MonitorRule._regions.contains(region)).all()
        for r in rules:
            for r_trigger in r._triggers:
                '''
                基于trigger, 从ES中取数据基于trigger.period 
                '''
                time_int = TimeInt[r_trigger.time]
                stoptime = datetime.datetime.strptime(req_data['time'], '%Y-%m-%d %H:%M:%S')
                t_delta = PeriodInt[r_trigger.period] * time_int
                starttime = stoptime + datetime.timedelta(minutes=-t_delta)
                history_data = es_client.get_record(
                        settings.opt['ELASTICSEARCH']['INDEX'],
                        starttime, stoptime, 
                        req_data['province'], req_data['county'],
                        req_data['broadband'], req_data['server'], req_data['app_id'],
                        PeriodInt[r_trigger.period], r_trigger._item.name
                        )
                logger.debug('{0}'.format(r_trigger._item.name))
                logger.debug('{0}'.format(history_data))
                logger.debug('{0}'.format(r_trigger.time))
                alert_ret = MonitorAlertHandler.alert_check(
                    history_data,
                    time_int,
                    r_trigger.threshold,
                    r_trigger.compare
                )
                if alert_ret is True:
                    alert_result.append({
                        'alert': True, 'trigger': r_trigger, 'region':r, 'data': history_data[1:]
                        })
                else:
                    alert_result.append({
                        'alert': False, 'trigger': r_trigger, 'region':r, 'data': history_data[1:]
                        })
        return alert_result

    @staticmethod
    def alert_check(data_list, last_time, threshold, compare):
        if last_time > len(data_list):
            return False
        for value in data_list[0:last_time]:
            if compare == '>':
                ret = True if value > threshold else False
            elif compare == '<':
                ret = True if value < threshold else False
            else:
                ret = True if value == threshold else False
            if not ret:
                break
        return ret

    '''
    trig_id: MonitorTrigger id
    output:
        告警已经确认: True
        告警未确认: False
    '''
    def check_confirm(self, trig_id, ip, province, county, broadband, appid):
        flag = 'cfm:{0};{1};{2};{3};{4};{5}'.format(trig_id, ip, province, county, broadband, appid)
        time_pre = self.redis.get_data(flag)
        if not time_pre:
            return False
        return True

    '''
    input: MonitorTrigger instance
    output:
        在重复时间段内: 'in_repeat'
        不在重复时间段内: 'out_repeat'
        之前无告警: 'no_alert'
    '''
    def check_alert(self, trig, ip, province, county, broadband, appid, time_now):
        if trig.repeat == 'no_repeat':
            return 'out_repeat'
        flag = 'trig:{0};{1};{2};{3};{4};{5}'.format(trig.id, ip, province, county, broadband, appid)
        time_pre = self.redis.get_data(flag) 
        if not time_pre:
            self.redis.set_data(flag, time_now)
            return 'no_alert'
        get_time = datetime.datetime.strptime
        time_delta = get_time(time_now, '%Y-%m-%d %H:%M:%S') - get_time(time_pre, '%Y-%m-%d %H:%M:%S')
        if time_delta.seconds > RepeatInt[trig.repeat] * 60:
            self.redis.set_data(flag, time_now)
            return 'out_repeat'
        return 'in_repeat'

    '''
    input: MonitorTrigger instance
    output:
        之前处于报警状态: True
        之前不处于报警状态: False
    '''
    def cancel_alert(self, trig_id, ip, province, county, broadband, appid):
        flag = 'trig:{0};{1};{2};{3};{4};{5}'.format(trig_id, ip, province, county, broadband, appid)
        time_pre = self.redis.del_data(flag)
        if not time_pre:
            return False
        flag_cfm = 'cfm:{0};{1};{2};{3};{4};{5}'.format(trig_id, ip, province, county, broadband, appid)
        # 删除报警确认信息
        self.redis.del_data(flag_cfm)
        self.redis.del_data(flag)
        return True

    @staticmethod
    def request_data_format(req_data):
        key_list = ['province', 'country', 'county', 'server', 'delay', 'loss_rate', 'time',
                'broadband', 'counter', 'app_id', 'max_delay', 'min_delay', 'type', 'devices']
        ret_data = {k: v for k, v in req_data.iteritems() if k in key_list}
        if ret_data['broadband'] not in CarrierList:
            ret_data['broadband'] = u'其他'.encode('utf-8')
        return ret_data

    @except_handler()
    def post(self, request_data):
        req_data = MonitorAlertHandler.request_data_format(request_data)
        es_client.create_record(settings.opt['ELASTICSEARCH']['INDEX'], req_data)
        trigger_alert = self.alert_handler(req_data)
        for _trig in trigger_alert:
            logger.debug('{0}'.format(_trig))
        for trig_l in trigger_alert:
            if trig_l['alert']:
                '''
                检查是否需要告警，报警邮件发送的两个条件:
                    用户未确认
                    在重复周期内
                一个告警日志记录由：
                trigger.id、服务器IP、省份、县市、运营商、app_id，共同识别
                '''
                ret_alert = self.check_alert(
                        trig_l['trigger'], req_data['server'], 
                        req_data['province'], req_data['county'], req_data['broadband'],
                        req_data['app_id'], req_data['time'])
                if ret_alert == 'no_alert':
                    '''
                    之前无告警，需要保存告警信息到告警日志
                    '''
                    logger.debug('create_alert_log:{0}, {1}, {2}'.format(
                        trig_l['trigger'].id, req_data['server'], req_data['time']))
                    content_detail = u'[{}]的线路出现告警，问题为：[{}异常]<br/>' \
                                     u'告警策略详情：<br/>' \
                                     u'指标：{}，触发条件：{}{}{}，统计周期：{}，持续时间：{}<br/>' \
                                     u'告警数值：<br/>' \
                                     u'{}({})'.format(
                        # req_data['time'],
                        # trig_l['region'].name,
                        # req_data['server'],
                        # u'{0}, {1}'.format(req_data['province'], req_data['county']),
                        req_data['broadband'],
                        trig_l['trigger']._item.comment,    # {6}
                        # trig_l['trigger']._rule.name,
                        trig_l['trigger']._item.comment,
                        trig_l['trigger'].compare,
                        trig_l['trigger'].threshold,
                        trig_l['trigger']._item.unit,       # {10}
                        trig_l['trigger'].period,
                        trig_l['trigger'].time,             # {12}
                        ['{:.2f}'.format(i) for i in trig_l['data']],
                        trig_l['trigger']._item.unit,
                    )
                    instance_ma = MonitorAlertLog(
                            start_time=req_data['time'],
                            trigger='{0}'.format(trig_l['trigger'].id),
                            rule_name=trig_l['trigger']._rule.name,
                            region=trig_l['region'].name,
                            province=req_data['province'].encode('utf8'),
                            county=req_data['county'].encode('utf8'),
                            broadband=req_data['broadband'].encode('utf8'),
                            appid=req_data['app_id'],
                            serverip=req_data['server'],
                            state='open',
                            content=trig_l['trigger']._item.comment.encode('utf8'),
                            content_detail=content_detail.encode('utf8'),
                            )
                    instance_ma._save(self.db_session)
                elif ret_alert == 'in_repeat':
                    continue
                else:
                    pass
                ret_cfm = self.check_confirm(trig_l['trigger'].id, req_data['server'], req_data['province'], req_data['county'],
                        req_data['broadband'], req_data['app_id'])
                if ret_cfm:
                    continue
                message = u'[{0}]，您的[{1}]集群下IP为[{2}]的服务器连接[{3}]地区[{4}]的线路出现告警，问题为：\r\n[{5}异常]\r\n' \
                          u'告警策略详情：\r\n' \
                          u'名称：{6}, 指标：{7}，触发条件：{8}{9}{10}，统计周期：{11}，持续时间：{12}\r\n' \
                          u'当前数值：\r\n' \
                          u'{13}({10})\r\n' \
                          u'请及时处理，更多详细信息请至控制台查看。'.format(
                    req_data['time'],
                    trig_l['region'].name,
                    req_data['server'],
                    u'{0}, {1}'.format(req_data['province'], req_data['county']),
                    req_data['broadband'],
                    u'{0}'.format(trig_l['trigger']._item.comment), # {6}
                    trig_l['trigger']._rule.name,
                    trig_l['trigger']._item.comment,
                    trig_l['trigger'].compare,
                    trig_l['trigger'].threshold,
                    trig_l['trigger']._item.unit,       # {10}
                    trig_l['trigger'].period,
                    trig_l['trigger'].time,             # {12}
                    ['{:.2f}'.format(i) for i in trig_l['data']],
                )
                # logger.debug('alert_mail:{0}, {1}, {2}'.format(
                #     trig_l['trigger'].id, req_data['server'], req_data['time']))
                for action in trig_l['trigger']._rule._actions:
                    send_mail(action.mail, action.contacter, message)
            else:
                '''
                检查是否需要取消告警
                '''
                ret_alert = self.cancel_alert(trig_l['trigger'].id, req_data['server'], req_data['province'],
                        req_data['county'], req_data['broadband'], req_data['app_id'])
                if ret_alert:
                    '''
                    更新告警日志，保存本次告警信息
                    发送取消告警消息
                    '''
                    al_records = self.db_session.query(MonitorAlertLog).filter(
                            MonitorAlertLog.rule_name==trig_l['trigger']._rule.name,
                            MonitorAlertLog.trigger=='{0}'.format(trig_l['trigger'].id),
                            MonitorAlertLog.serverip==req_data['server'],
                            MonitorAlertLog.province==req_data['province'].encode('utf8'),
                            MonitorAlertLog.county==req_data['county'].encode('utf8'),
                            MonitorAlertLog.broadband==req_data['broadband'].encode('utf8'),
                            MonitorAlertLog.appid==req_data['app_id'],
                            or_(MonitorAlertLog.state=='open', MonitorAlertLog.state=='confirm'),
                            ).all()
                    for al_record in al_records:
                        al_record.state = 'close'
                        al_record.stop_time = req_data['time']
                        al_record.content_detail = u'{}<br/>' \
                                            u'线路恢复正常，告警取消。<br/>' \
                                            u'当前数值：<br/>' \
                                            u'{}({})'.format(
                            al_record.content_detail,
                            ['{:.2f}'.format(i) for i in trig_l['data']],
                            trig_l['trigger']._item.unit,
                        ).encode('utf8')
                        al_record._save(self.db_session, update=True, commit=False)
                    self.db_session.commit()
                    message = u'[{0}]，您的[{1}]集群下IP为[{2}]的服务器连接[{3}]地区[{4}]的线路恢复正常，原告警问题描述为：\r\n[{5}异常]\r\n' \
                              u'触发告警策略详情：\r\n' \
                              u'名称：{6}, 指标：{7}，触发条件：{8}{9}{10}，统计周期：{11}，持续时间：{12}\r\n' \
                              u'当前数值：\r\n' \
                              u'{13}({10})\r\n' \
                              u'更多详细信息请至控制台查看。'.format(
                        req_data['time'],
                        trig_l['region'].name,
                        req_data['server'],
                        u'{0}, {1}'.format(req_data['province'], req_data['county']),
                        req_data['broadband'],
                        u'{0}'.format(trig_l['trigger']._item.comment),     # {6}
                        trig_l['trigger']._rule.name,
                        trig_l['trigger']._item.comment,
                        trig_l['trigger'].compare,
                        trig_l['trigger'].threshold,
                        trig_l['trigger']._item.unit,       # {10}
                        trig_l['trigger'].period,
                        trig_l['trigger'].time,             # {12}
                        ['{:.2f}'.format(i) for i in trig_l['data']],
                    )
                    # logger.debug('cansel_alert_mail:{0}, {1}, {2}'.format(
                    #     trig_l['trigger'].id, req_data['server'], req_data['time']))
                    for action in trig_l['trigger']._rule._actions:
                        send_mail(action.mail, action.contacter, message)
        return {'return': 0}
