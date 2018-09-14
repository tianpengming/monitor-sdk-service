# -*- encoding:utf-8 -*-

import datetime
from utils.es_base import ESBase, TIMEOUT
import logging
logger = logging.getLogger()

BD_LIST = [u'移动', u'联通', u'电信']

class ESInterface(ESBase):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.type_name = 'records'
        self.type_template = {
            'mappings': {
                self.type_name: {
                    'properties': {
                        'time': {'type': 'date',
                            'format': 'yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis'},
                        'province': {'type': 'string', 'index': 'not_analyzed', 'store': 'true'},
                        'country': {'type': 'string', 'index': 'not_analyzed', 'store': 'true'},
                        'county': {'type': 'string', 'index': 'not_analyzed', 'store': 'true'},
                        'server': {'type': 'ip', 'store': 'true'},
                        'delay': {'type': 'float', 'index': 'not_analyzed', 'store': 'true'},
                        'loss_rate': {'type': 'float', 'index': 'not_analyzed', 'store': 'true'},
                        'broadband': {'type': 'string', 'index': 'not_analyzed', 'store': 'true'},
                        'counter': {'type': 'integer', 'index': 'not_analyzed', 'store': 'true'},
                        'app_id': {'type': 'string', 'index': 'not_analyzed', 'store': 'true'},
                        'max_delay': {'type': 'float', 'index': 'not_analyzed', 'store': 'true'},
                        'min_delay': {'type': 'float', 'index': 'not_analyzed', 'store': 'true'},
                        'type': {'type': 'string', 'index': 'not_analyzed', 'store': 'true'},
                        'devices': {'type': 'integer', 'index': 'not_analyzed', 'store': 'true'},
                        }
                    }
                }
            }

    def get_record(
            self, userid,
            start_time, stop_time,
            province,
            county,
            broadband,
            server,
            app_id,
            interval,
            name,
            ):
        index_list = [userid.lower()]
        # start_index = '{}_{}'.format(userid.lower(), start_time.strftime('%Y%m%d'))
        # stop_index = '{}_{}'.format(userid.lower(), stop_time.strftime('%Y%m%d'))
        # if start_index != stop_index:
        #     for i in [start_index, stop_index]:
        #         if self.es_con.indices.exists(index=i) is True:
        #             index_list.append(i)
        # else:
        #     if self.es_con.indices.exists(index=start_index) is True:
        #         index_list.append(start_index)
        req_dsl = {
            'size': 0,
            'query': {
                'bool': {
                    'filter': [
                        {'range': {
                            'time': {
                                'gte': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'lte': stop_time.strftime('%Y-%m-%d %H:%M:%S')
                            }
                        }
                        },
                    ],
                    'must': [
                        {'term': {'province': province}},
                        {'term': {'server': server}},
                        {'term': {'app_id': app_id}},
                        {'term': {'county': county}},
                        {'term': {'broadband': broadband}},
                    ]
                }
            },
            'aggs': {
                'by_time': {
                    'date_histogram': {
                        'field': 'time',
                        'interval': '{0}m'.format(interval),
                        # 'format': 'yyyy-MM-dd hh:mm:ss',
                        'min_doc_count': 0,
                        'extended_bounds': {
                            'min': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'max': stop_time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    },
                    'aggs': {
                        'value_sum': {
                            'sum': {'field': name}
                        }
                    },
                },
            },
        }
        ret_data = self.es_con.search(index=','.join(index_list),
                                      doc_type=self.type_name,
                                      body=req_dsl,
                                      params={'request_timeout':TIMEOUT}
                                      )
        # logger.debug('{0}'.format(ret_data))
        return [item['value_sum']['value'] / item['doc_count'] 
                for item in ret_data['aggregations']['by_time']['buckets']
                if item['doc_count'] != 0
                ]

    def get_region_record(
            self, userid,
            starttime, stoptime,
            broadband,
            servers,
            datatype,
            ):
        index_list = [userid.lower()]
        # start_index = '{}_{}'.format(userid.lower(), start_time.strftime('%Y%m%d'))
        # stop_index = '{}_{}'.format(userid.lower(), stop_time.strftime('%Y%m%d'))
        # if start_index != stop_index:
        #     for i in [start_index, stop_index]:
        #         if self.es_con.indices.exists(index=i) is True:
        #             index_list.append(i)
        # else:
        #     if self.es_con.indices.exists(index=userid) is True:
        #         index_list.append(start_index)
        other = False
        if u'其他'.encode() in broadband:
            other = True
        must_list = [i for i in broadband if i in BD_LIST]
        must_not_list = [i for i in BD_LIST if i not in broadband]
        req_dsl = {
                'size': 0,
                'query': {
                    'bool': {
                        'filter': [
                            {'range': {
                                'time': {
                                    'gte': starttime.strftime('%Y-%m-%d %H:%M:%S'),
                                    'lte': stoptime.strftime('%Y-%m-%d %H:%M:%S')
                                    }
                                }
                            },
                            {'terms': {'server': servers}},
                            ],
                        # 'must': [{'terms': {'broadband': must_list}}],
                    },
                },
                'aggs': {
                    'per_province_sum': {
                        'terms': {'field': 'province', 'size': 0},
                        'aggs': {
                            'counter_sum': {'sum': {'field': 'counter'}},
                        },
                    }
                }
        }
        if datatype=='delay' or datatype=='all':
            req_dsl['aggs']['per_province_sum']['aggs']['delay_sum'] = {'sum': {'script': "doc['delay'].value * doc['counter'].value"}}
        if datatype=='loss_rate' or datatype=='all':
            req_dsl['aggs']['per_province_sum']['aggs']['loss_sum'] = {'sum': {'script': "doc['loss_rate'].value * doc['counter'].value"}}
        if other is not True:
            req_dsl['query']['bool']['must'] = [{'terms': {'broadband': must_list}}]
        else:
            req_dsl['query']['bool']['must_not'] = [{'terms': {'broadband': must_not_list}}]
        ret_data = self.es_con.search(index=','.join(index_list),
                                      doc_type=self.type_name,
                                      body=req_dsl,
                                      params={'request_timeout':TIMEOUT}
                                      )
        if datatype=='delay':
            return [{'province': item['key'],
                'delay': round(item['delay_sum']['value'] / item['counter_sum']['value'])}
                for item in ret_data['aggregations']['per_province_sum']['buckets']
                ] 
        elif datatype=='loss_rate':
            return [{'province': item['key'],
                'loss_rate': round(item['loss_sum']['value'] / item['counter_sum']['value'], 1),
                }
                for item in ret_data['aggregations']['per_province_sum']['buckets']
                ] 
        else:
            return [{'province': item['key'],
                'loss_rate': round(item['loss_sum']['value'] / item['counter_sum']['value'], 1),
                'delay': round(item['delay_sum']['value'] / item['counter_sum']['value'])}
                for item in ret_data['aggregations']['per_province_sum']['buckets']
                ] 

    def get_province_record(
            self, userid,
            starttime, stoptime,
            broadband,
            servers,
            province,
            ):
        userid = userid.lower()
        must_list = [i for i in broadband if i in BD_LIST]
        must_not_list = [i for i in BD_LIST if i not in broadband]
        other = False
        if u'其他'.encode() in broadband:
            other = True
        req_dsl = {
            'size': 1,
            'query': {
                'bool': {
                    'filter': [{
                        'range': {
                            'time': {
                                'gte': starttime.strftime('%Y-%m-%d %H:%M:%S'),
                                'lte': stoptime.strftime('%Y-%m-%d %H:%M:%S')
                            }
                        }
                    },
                        {'terms': {'server': servers}},
                    ],
                    'must': [
                        # {'terms': {'broadband': broadband}},
                        {'term': {'province': province}},
                    ]
                },
            },
            'sort': {
                'time': {'order': 'desc'}
            },
            'aggs': {
                'per_county_sum': {
                    'terms': {'field': 'county', 'size': 0},
                    'aggs': {
                        'counter_sum': {'sum': {'field': 'counter'}},
                    },
                }
            }
        }
        req_dsl['aggs']['per_county_sum']['aggs']['delay_sum'] = {'sum': {'script': "doc['delay'].value * doc['counter'].value"}}
        req_dsl['aggs']['per_county_sum']['aggs']['loss_sum'] = {'sum': {'script': "doc['loss_rate'].value * doc['counter'].value"}}
        if other is not True:
            req_dsl['query']['bool']['must'].append({'terms': {'broadband': must_list}})
        else:
            req_dsl['query']['bool']['must_not'] = [{'terms': {'broadband': must_not_list}}]
        ret_data = self.es_con.search(index=userid,
                                      doc_type=self.type_name,
                                      body=req_dsl,
                                      params={'request_timeout':TIMEOUT}
                                      )
        # logger.debug('{0}'.format(ret_data))
        if not ret_data['hits']['hits']:
            return {'updatetime': None, 'county_net': []}
        updatetime = ret_data['hits']['hits'][0]['_source']['time']
        return {'updatetime': updatetime,
                'county_net': [
                    {'county': item['key'],
                    'loss_rate': round(item['loss_sum']['value'] / item['counter_sum']['value'], 1),
                    'delay': round(item['delay_sum']['value'] / item['counter_sum']['value'], 1),
                    'counter': item['counter_sum']['value'],
                    }
                    for item in ret_data['aggregations']['per_county_sum']['buckets']
                    ] 
                }


es_client = ESInterface()
