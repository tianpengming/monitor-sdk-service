# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from tornado.web import RequestHandler, MissingArgumentError
from werkzeug.datastructures import MultiDict
import json
import datetime

from model.common import Session
from model.rule import (
        MonitorItem, MonitorTrigger, MonitorRule, MonitorContact,
        )
from model.rule_form import MonitorRuleForm
from utils.exceptions import Status400, Status403, except_handler
from utils.serializer import AlchemyEncoder
from utils.es_interface import es_client
# from conf import settings

class MonitorItemHandler(RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(MonitorItemHandler, self).__init__(
                application, request, **kwargs)
        self.db_session = Session()

    def __del__(self):
        self.db_session.close()

    @except_handler()
    def get(self, req_data):
        data_list = self.db_session.query(MonitorItem).all()
        serialized = [
                AlchemyEncoder().parse_sqlalchemy_object(item)
                for item in data_list
                ]
        return {'instance': serialized, 'result': 0, 'message': 'success'}


class MonitorRuleHandler(RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(MonitorRuleHandler, self).__init__(
                application, request, **kwargs)
        self.db_session = Session()

    def __del__(self):
        self.db_session.close()

#     @except_handler()
    # def get(self, req_data):
        # data_list = self.db_session.query(MonitorRule).all()
        # serialized = []
        # for rule in data_list:
            # triggers = [AlchemyEncoder().parse_sqlalchemy_object(item) for item in rule._triggers]
            # regions = [item.id for item in rule._regions]
            # actions = [AlchemyEncoder().parse_sqlalchemy_object(item) for item in rule._actions]
            # serialized.append(
                    # {'id':rule.id, 'triggers':triggers, 'regions':regions,
                        # 'actions':actions, 'name':rule.name}
                    # )
#         return {'instance': serialized, 'result': 0, 'message': 'success'}

    @except_handler()
    def get(self, req_data):
        data_list = self.db_session.query(MonitorRule).all()
        serialized = []
        for rule in data_list:
            triggers = []
            for item in rule._triggers:
                triggers.append({
                    'id':item.id, 'period':item.period, 'time':item.time, 'repeat':item.repeat,
                    'compare':item.compare, 'threshold':item.threshold, 'update_time':item.update_time,
                    'item':{
                        'id':item._item.id, 'name':item._item.name,
                        'comment':item._item.comment, 'unit':item._item.unit}
                    })
            regions = [item.id for item in rule._regions]
            actions = [AlchemyEncoder().parse_sqlalchemy_object(item) for item in rule._actions]
            serialized.append({'id':rule.id, 'triggers':triggers, 'regions':regions,
                        'actions':actions, 'name':rule.name
                        })
        return {'instance': serialized, 'result': 0, 'message': 'success'}

    @except_handler()
    def post(self, req_data):
        form = MonitorRuleForm(data=MultiDict(req_data))
        if not form.validate():
            raise Status400(form.errors)
        result = MonitorRule._validate(self.db_session, **req_data)
        instance = result['instance']
        if instance is None:
            raise Status403(result['message'])
        instance._save(self.db_session)
        return {'instance': AlchemyEncoder().parse_sqlalchemy_object(instance),
            'result': 0, 'message': 'success'}

    '''
    删除告警策略中的告警规则，每条告警规则只属于一个告警策略
    '''
    @except_handler()
    def delete(self, req_data):
        if not req_data.has_key('id'):
            raise Status400('id is required')
        result = MonitorTrigger._validate(self.db_session, req_data['id'])
        instance = result['instance']
        if instance is None:
            raise Status403(result['message'])
        if len(instance._rule._triggers) == 1:
            # 删除整条告警规则
            for i in instance._rule._actions:
                i._delete(self.db_session, commit=False)
            instance._rule._delete(self.db_session, commit=False)
        instance._delete(self.db_session)
        return {'id': '{}'.format(instance.id),
           'result': 0, 'message': 'success',
           }

    '''
    删除整条告警策略
    '''
#     @except_handler()
    # def delete(self, req_data):
        # if not req_data.has_key('id'):
            # raise Status400('id is required')
        # result = MonitorRule._validate(self.db_session, req_data['id'])
        # instance = result['instance']
        # if instance is None:
            # raise Status403(result['message'])
        # instance._actions._delete(self.db_session)
        # instance._triggers._delete(self.db_session)
        # instance._delete(self.db_session)
        # return {'id': '{}'.format(instance.id),
#            'result': 0, 'message': 'success',
           # }

# class MonitorContactHandler(RequestHandler):

    # def __init__(self, application, request, **kwargs):
        # super(MonitorContactHandler, self).__init__(
                # application, request, **kwargs)
        # self.db_session = Session()

    # @except_handler()
    # def get(self, req_data):
        # form = MonitorPostContactForm(MultiDict(req_data))
        # if not form.validate():
            # # raise Status400(form.errors)
            # return form.errors
        # data_list = self.db_session.query(MonitorContact).all()
        # serialized = [
                # AlchemyEncoder().parse_sqlalchemy_object(item)
                # for item in data_list
                # ]
        # return {'instance': serialized, 'result': 0, 'message': 'success'}

    # @except_handler()
    # def post(self, req_data):
        # form = MonitorPostContactForm(MultiDict(req_data))
        # if not form.validate():
            # # raise Status400(form.errors)
            # return form.errors
        # result = MonitorContact._validate(self.db_session, **form.data)
        # instance = result['instance']
        # if instance is None:
            # raise Status403(result['message'])
        # instance._save(self.db_session)
        # return {'instance': AlchemyEncoder().parse_sqlalchemy_object(instance),
            # 'result': 0, 'message': 'success'}

    # @except_handler()
    # def put(self, req_data):
        # if not req_data.has_key('id'):
            # raise Status400('id is required')
        # form = MonitorPostContactForm(MultiDict(req_data))
        # if not form.validate():
            # raise Status400(form.errors)
        # result = MonitorContact._validate(self.db_session, req_data['id'], **form.data)
        # instance = result['instance']
        # if instance is None:
            # raise Status403(result['message'])
        # instance._save(self.db_session, update=True)
        # return {
            # 'instance': AlchemyEncoder().parse_sqlalchemy_object(instance),
            # 'result': 0, 'message': 'success',
            # }

    # @except_handler()
    # def delete(self, req_data):
        # if not req_data.has_key('id'):
            # raise Status400('id is required')
        # result = MonitorContact._validate(self.db_session, req_data['id'])
        # instance = result['instance']
        # if instance is None:
            # raise Status403(result['message'])
        # instance._delete(self.db_session)
        # return {'id': '{}'.format(instance.id),
           # 'result': 0, 'message': 'success',
#            }
