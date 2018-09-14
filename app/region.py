# -*- coding:utf-8 -*-

from tornado.web import RequestHandler, MissingArgumentError
from werkzeug.datastructures import ImmutableMultiDict

from model.region import (
        MonitorServerIpForm, MonitorServerIp,
        MonitorRegion, MonitorRegionPostForm, MonitorRegionPutForm
        )
from model.common import Session
from utils.exceptions import Status400, Status403, except_handler
from utils.serializer import AlchemyEncoder

class MonitorServerIpHandler(RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(MonitorServerIpHandler, self).__init__(
                application, request, **kwargs)
        self.db_session = Session()

    def __del__(self):
        self.db_session.close()

    @except_handler()
    def get(self, req_data):
        data_list = self.db_session.query(MonitorServerIp).filter(
                MonitorServerIp._region_id==None)
        serialized = [
                AlchemyEncoder().parse_sqlalchemy_object(item)
                for item in data_list
                ]
        return {'instance': serialized, 'result': 0, 'message': 'success'}

    @except_handler()
    def post(self, req_data):
        form = MonitorServerIpForm(ImmutableMultiDict(req_data))
        if not form.validate():
            raise Status400(form.errors)
        result = MonitorServerIp._validate(self.db_session, **req_data)
        instance = result['instance'] 
        if instance is None:
            raise Status403(result['message'])
        instance._save(self.db_session)
        return {'instance': AlchemyEncoder().parse_sqlalchemy_object(instance),
                'result': 0, 'message': 'success'}

    '''
    支持多个ServerIp删除
    '''
    @except_handler()
    def delete(self, req_data):
        if not req_data.has_key('id'):
            raise Status400('id is required')
        failed = []
        success = []
        for ip_id in req_data['id']:
            result = MonitorServerIp._validate(self.db_session, ip_id)
            instance = result['instance']
            if instance is None:
                failed.append(ip_id)
            else:
                success.append(ip_id)
                instance._delete(self.db_session)
        return {'result': 0, 'message': 'success',
           'success': success, 'failed': failed
           }

#     @except_handler()
    # def delete(self, req_data):
        # if not req_data.has_key('id'):
            # raise Status400('id is required')
        # result = MonitorServerIp._validate(self.db_session, req_data['id'])
        # instance = result['instance']
        # if instance is None:
            # raise Status403(result['message'])
        # instance._delete(self.db_session)
        # return {'id': '{}'.format(instance.id),
           # 'result': 0, 'message': 'success',
#            }

class MonitorRegionHandler(RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(MonitorRegionHandler, self).__init__(
                application, request, **kwargs)
        self.db_session = Session()

    def __del__(self):
        self.db_session.close()

    @except_handler()
    def get(self, req_data):
        data_list = self.db_session.query(MonitorRegion).all()
        serialized = [
                AlchemyEncoder().parse_sqlalchemy_object(item)
                for item in data_list
                ]
        return {'instance': serialized, 'result': 0, 'message': 'success'}

    @except_handler()
    def post(self, req_data):
        form = MonitorRegionPostForm(data=ImmutableMultiDict(req_data))
        if not form.validate():
            raise Status400(form.errors)
        result = MonitorRegion._validate(self.db_session, **req_data)
        instance = result['instance']
        if instance is None:
            raise Status403(result['message'])
        instance._save(self.db_session)
        return {'instance': AlchemyEncoder().parse_sqlalchemy_object(instance),
                'result': 0, 'message': 'success'}

    @except_handler()
    def put(self, req_data):
        if not req_data.has_key('id'):
            raise Status400('id is required')
        form = MonitorRegionPutForm(data=ImmutableMultiDict(req_data))
        if not form.validate():
            raise Status400(form.errors)
        result = MonitorRegion._validate(self.db_session, req_data['id'], **req_data)
        instance = result['instance']
        if instance is None:
            raise Status403(result['message'])
        instance._save(self.db_session)
        return {'id': '{}'.format(instance.id),
           'result': 0, 'message': 'success'}

    @except_handler()
    def delete(self, req_data):
        if not req_data.has_key('id'):
            raise Status400('id is required')
        result = MonitorRegion._validate(self.db_session, req_data['id'])
        instance = result['instance']
        if instance is None:
            raise Status403(result['message'])
        instance._delete(self.db_session)
        return {'id': '{}'.format(instance.id),
           'result': 0, 'message': 'success'}

class MonitorRegionServerIpHandler(RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(MonitorRegionServerIpHandler, self).__init__(
                application, request, **kwargs)
        self.db_session = Session()

    def __del__(self):
        self.db_session.close()

    @except_handler()
    def get(self, req_data):
        if not req_data.has_key('id'):
            raise Status400('id is required')
        result = MonitorRegion._validate(self.db_session, req_data['id'])
        if result['instance'] is None:
            raise Status403(result['message'])
        serialized = [
                AlchemyEncoder().parse_sqlalchemy_object(item)
                for item in result['instance']._serverips
                ]
        return {'instance': serialized, 'result': 0, 'message': 'success'}
