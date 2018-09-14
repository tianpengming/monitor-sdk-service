from conf import settings
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import logging
logger = logging.getLogger()

TIMEOUT = 60

class ESBase(object):

    def __init__(self):
        host = settings.opt['ELASTICSEARCH']['HOST']
        self.es_con = Elasticsearch(
                settings.opt['ELASTICSEARCH']['HOST'],
                port=settings.opt['ELASTICSEARCH']['PORT']
                )
        self.type_name = 'example'
        self.type_template = {
            'settings': {
                'index': {
                    'number_of_shards': 15,
                    'number_of_replicas': 2,
                }
            },
            'mappings': {
                self.type_name: {
                    'properties': {
                         'timestamp': {'type': 'date',
                            'format': 'yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis'},
                         }
                    }
                }
            }
        self.update_template = None

    def get_index(self):
        ret_index = self.es_con.cat.indices()
        index_list = [i['index'] for i in ret_index]
        return index_list

    def delete_index(self, index):
        index = index.lower()
        if self.es_con.indices.exists(index=index) is True:
            ret_data = self.es_con.indices.delete(index=index)
            if ret_data != {'acknowledged': True}:
                return {'result': False, 'message': '{}'.format(ret_data)}
        return {'result': True, 'message': 'success'}

    def create_index(self, index):
        index = index.lower()
        if self.es_con.indices.exists(index=index) is not True:
            ret_data = self.es_con.indices.create(index=index, body=self.type_template)
            if ret_data != {'acknowledged': True}:
                return {'result': False, 'message': '{}'.format(ret_data)}
        return {'result': True, 'message': 'success'}

    def update_index(self, index):
        index = index.lower()
        if not self.update_template:
            return {'result': False, 'message': 'empty update template'}
        if self.es_con.indices.exists(index=index) is True:
            ret_data = self.es_con.indices.put_mapping(index=index, doc_type=self.type_name, body=self.update_template)
            if ret_data != {'acknowledged': True}:
                return {'result': False, 'message': '{}'.format(ret_data)}
        return {'result': True, 'message': 'success'}

    def create_record(self, index, item):
        index = index.lower()
        ret_data = self.es_con.index(index=index, doc_type=self.type_name, body=item, refresh=True)
        if ret_data['created']:
            return {'result': 0, 'message': None}
        else:
            return {'result': -1, 'message': '{0}'.format(ret_data)}
