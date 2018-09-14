from utils.es_base import ESBase, TIMEOUT
import datetime
import logging
logger = logging.getLogger()

ESSIZEMAX = 10000
HEARTDEALYMAX = 999

class ESAccount(ESBase):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.type_name = "logs"
        self.type_template = {
            "mappings": {
                self.type_name: {
                    "properties": {
                        "app_id": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "user_id": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "user_name": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "server_name": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "log_type": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "update_time": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
                        },
                    }
                }
            }
        }

    def get_record(
            self, index,
            startpos,
            length,
            userid=None,
            username=None,
            servername=None,
    ):
        index = index.lower()
        req_dsl = {
                "from": startpos,
                "size": length,
                "query": {
                    "filtered": {
		                "query": {"match_all": {}},
                        "filter": {"bool": {"must": []}}
                        }
                    },
                "sort": {
                    "update_time": {"order": "asc"}
                },
        }
        if userid is not None:
            req_dsl["query"]["filtered"]["filter"]["bool"]["must"].append(
                {"query": {"wildcard": {"user_id": "*{0}*".format(userid)}}})
        if username is not None:
            req_dsl["query"]["filtered"]["filter"]["bool"]["must"].append(
                {"query": {"wildcard": {"user_name": "*{0}*".format(username)}}})
        if servername is not None:
            req_dsl["query"]["filtered"]["filter"]["bool"]["must"].append(
                {"query": {"wildcard": {"server_name": "*{0}*".format(servername)}}})
        req_data = self.es_con.search(index=index, doc_type=self.type_name, body=req_dsl, params={"request_timeout":TIMEOUT})
        hits = []
        maxlen = req_data["hits"].get("total", 10)
        for item in req_data["hits"]["hits"]:
            hits.append({
                "userid": item['_source']['user_id'],
                "username": item["_source"]["user_name"],
                "server_name": item["_source"]["server_name"],
                'appid': item['_source']['app_id'],
            })

        return {'instance': hits, 'maxlen': maxlen}


class ESUserQuery(ESBase):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.type_name = "logs"
        self.type_template = {
            "mappings": {
                self.type_name: {
                    "properties": {
                        "start_time": {"type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"},
                        "app_id": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "remote_ip": {"type": "ip", "store": "true"},
                        "log_type": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "game_num": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "user_id": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "user_name": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "dur_time": {"type": "float", "index": "not_analyzed", "store": "true"},
                        "server_name": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "target_ip": {"type": "ip", "store": "true"},
                        "device_id": {"type": "string", "index": "not_analyzed", "store": "true"},
                        }
                    }
                }
            }

    # def get_record(
    #         self, index,
    #         startpos,
    #         length,
    #         userid=None,
    #         username=None,
    #         servername=None,
    #         ):
    #     index = index.lower()
    #     req_dsl = {
    #             "size": 0,
    #             "query": {
    #                 "filtered": {
		#                 "query": {"match_all": {}},
    #                     "filter": {"bool": {"must": []}}
    #                     }
    #                 },
    #                 "sort": {
    #                     "start_time": { "order": "desc" }
    #                     },
    #                 "aggs": {
    #                     "by_userid": {
    #                         "terms": {"field": "user_id", "size": 0},
    #                         "aggs": {
    #                             "by_server_name": {
    #                             "terms": {"field": "server_name"},
    #                             "aggs": {
    #                                 "by_appid": {
    #                                     "terms": {"field": "app_id"},
    #                                         "aggs": {
    #                                             "by_user_name": {
    #                                                 "terms": {"field": "user_name"}
    #                                                 }
    #                                             }
    #                                     }
    #                                 }
    #                             }
    #                         }
    #                     }
    #                 }
    #             }
    #     if userid is not None:
    #         req_dsl["query"]["filtered"]["filter"]["bool"]["must"].append(
    #             {"query": {"wildcard": {"user_id": "*{0}*".format(userid)}}}
    #         )
    #     if username is not None:
    #         req_dsl["query"]["filtered"]["filter"]["bool"]["must"].append(
    #             {"query": {"wildcard": {"user_name": "*{0}*".format(username)}}}
    #         )
    #     if servername is not None:
    #         req_dsl["query"]["filtered"]["filter"]["bool"]["must"].append(
    #             {"query": {"wildcard": {"server_name": "*{0}*".format(servername)}}}
    #         )
    #     req_data = self.es_con.search(index=index, doc_type=self.type_name, body=req_dsl, params={"request_timeout":TIMEOUT})
    #     hits = []
    #     for uid in req_data["aggregations"]["by_userid"]["buckets"]:
    #         for sname in uid["by_server_name"]["buckets"]:
    #             for aid in sname["by_appid"]["buckets"]:
    #                 for uname in aid["by_user_name"]["buckets"]:
    #                     hits.append({
    #                             "userid": uid["key"],
    #                             "username": uname["key"],
    #                             "appid": aid["key"],
    #                             "server_name": sname["key"],
    #                             })
    #     maxlen = len(hits)
    #     return {"maxlen": maxlen,
    #             "instance": hits[startpos:startpos+length]}

    def get_detail_record(
            self, index,
            userid, 
            server_name,
            appid,
            starttime, 
            stoptime,
            # username,
            ):
        index = index.lower()
        req_dsl = {
                "size": ESSIZEMAX,
                "query": {
                    "bool": {
                        "filter": [
                            {"range": {
                                "start_time": {
                                    "gte": starttime.strftime("%Y-%m-%d %H:%M:%S"),
                                    "lte": stoptime.strftime("%Y-%m-%d %H:%M:%S")
                                    }
                                }
                            },
                        ],
                    "must": [
                        {"term": {"server_name": server_name}},
                        # {"term": {"user_name": username}},
                        {"term": {"user_id": userid}},
                        {"term": {"app_id": appid}},
                        ]
                    }
                }
            }
        req_data = self.es_con.search(index=index, doc_type=self.type_name, body=req_dsl, params={"request_timeout":TIMEOUT})
        # logger.debug("{0}".format(ret_data))
        if not req_data["hits"]["hits"]:
            return {"instance": []}
        hits = []
        for item in req_data["hits"]["hits"]:
            item_tmp = {
                "game_id": "{0}+{1}".format(item["_source"]["game_num"], item["_source"]["start_time"]),
                "start_time": item["_source"]["start_time"],
                "duration": item["_source"]["dur_time"],
                "device_id": item["_source"]["device_id"],
                "target_ip": item["_source"]["target_ip"],
            }
            if item_tmp not in hits:
                hits.append(item_tmp)
        # hits = [{"game_id": "{0}+{1}".format(item["_source"]["game_num"], item["_source"]["start_time"]),
        #     "start_time": item["_source"]["start_time"],
        #     "duration": item["_source"]["dur_time"],
        #     "device_id": item["_source"]["device_id"],
        #     "target_ip": item["_source"]["target_ip"],
        #     }
        #     for item in req_data["hits"]["hits"]
        #     ]
#         device_id = req_data["hits"]["hits"][0]["_source"]["device_id"]
#         target_ip = req_data["hits"]["hits"][0]["_source"]["target_ip"]
#         maxlen = req_data["hits"]["total"]
        return {"instance": hits}

class ESHeartbeat(ESBase):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.type_name = "logs"
        self.type_template = {
            'settings': {
                'index': {
                    'number_of_shards': 7,
                    'number_of_replicas': 1,
                }
            },
            "mappings": {
                self.type_name: {
                    "properties": {
                        "timestamp": {"type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"},
                        "app_id": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "remote_ip": {"type": "ip", "store": "true"},
                        "device_id": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "target_ip": {"type": "ip", "store": "true"},
                        "net_type": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "log_type": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "min_delay": {"type": "float", "index": "not_analyzed", "store": "true"},
                        "max_delay": {"type": "float", "index": "not_analyzed", "store": "true"},
                        "mid_delay": {"type": "float", "index": "not_analyzed", "store": "true"},
                        "avg_delay": {"type": "float", "index": "not_analyzed", "store": "true"},
                        "lost_rate": {"type": "float", "index": "not_analyzed", "store": "true"},
                        "interval": {"type": "integer", "index": "not_analyzed", "store": "true"},
                        "delay_list": {"type": "float", "index": "not_analyzed", "store": "true"},
                        "delay_top": {"type": "float", "index": "not_analyzed", "store": "true"},
                        "real_time": {"type": "string", "index": "not_analyzed", "store": "true"},
                        }
                    }
                }
            }
        self.update_template = {
            self.type_name: {
                "properties": {
                    "delay_top": {"type": "float", "index": "not_analyzed", "store": "true"},
                    }
                }
            }

    def get_record(
            self, index,
            appid,
            device_id,
            start_time,
            duration,
            target_ip,
            user_id=None,
            ):
        index_list = [index.lower()]
        stop_time = start_time + datetime.timedelta(seconds=duration)
        start_index = '{}_{}'.format(index.lower(), start_time.strftime('%Y%m%d'))
        stop_index = '{}_{}'.format(index.lower(), stop_time.strftime('%Y%m%d'))
        if start_index != stop_index:
            for i in [start_index, stop_index]:
                if self.es_con.indices.exists(index=i) is True:
                    index_list.append(i)
        else:
            if self.es_con.indices.exists(index=index) is True:
                index_list.append(start_index)
        req_dsl = {
            "size": ESSIZEMAX,
            "query": {
                "bool": {
                    "filter": [
                        {"range": {
                            "timestamp": {
                                "gte": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                                "lte": stop_time.strftime("%Y-%m-%d %H:%M:%S")
                            }
                        }
                        },
                    ],
                    "must": [
                        {"term": {"device_id": device_id}},
                        {"term": {"app_id": appid}},
                        {"term": {"target_ip": target_ip}},
                    ]
                }
            }
        }
        req_data = self.es_con.search(index=','.join(index_list),
                                      doc_type=self.type_name,
                                      body=req_dsl,
                                      params={"request_timeout":TIMEOUT}
                                      )
        interval, delay_top = 0, 0
        req_list = list()
        for item in req_data["hits"]["hits"]:
            if interval == 0 or interval > item["_source"]["interval"]:
                interval = item["_source"]["interval"]
            if delay_top == 0 or delay_top < item["_source"].get("delay_top", HEARTDEALYMAX):
                delay_top = item["_source"].get("delay_top", HEARTDEALYMAX)
            req_list.append({
                "loss_rate": item["_source"]["lost_rate"],
                "delay_list": item["_source"]["delay_list"],
                "delay": item["_source"]["avg_delay"],
                "time": item["_source"]["timestamp"],
                "interval": item["_source"]["interval"],
                })
        return {"interval": interval,
                "delay_top": delay_top,
                "dlist": req_list
                }

class ESTrace(ESBase):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.type_name = "logs"
        self.type_template = {
            'settings': {
                'index': {
                    'number_of_shards': 3,
                    'number_of_replicas': 1,
                }
            },
            "mappings": {
                self.type_name: {
                    "properties": {
                        "timestamp": {"type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"},
                        "app_id": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "remote_ip": {"type": "ip", "store": "true"},
                        "user_id": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "user_name": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "channel": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "server_id": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "target_ip": {"type": "ip", "store": "true"},
                        "device_id": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "device_name": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "device_version": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "device_type": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "location": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "log_type": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "net_type": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "net_delay": {"type": "string", "index": "not_analyzed", "store": "true"},
                        "wifi_count": {"type": "integer", "index": "not_analyzed", "store": "true"},
                        "wifi_rssi": {"type": "integer", "index": "not_analyzed", "store": "true"},
                        "wifi_channel": {"type": "integer", "index": "not_analyzed", "store": "true"},
                        "frequency": {"type": "integer", "index": "not_analyzed", "store": "true"},
                        "speed": {"type": "integer", "index": "not_analyzed", "store": "true"},
                        "route_delay": {"type": "float", "index": "not_analyzed", "store": "true"},
                        "local_delay": {"type": "float", "index": "not_analyzed", "store": "true"},
                        "cell_rssi": {"type": "integer", "index": "not_analyzed", "store": "true"},
                        "cell_delay": {"type": "float", "index": "not_analyzed", "store": "true"},
                        "delay_top": {"type": "float", "index": "not_analyzed", "store": "true"},
                        "traceroute": {
                            "type": "nested",
                            "properties": {
                                "ip": {"type": "string", "index": "not_analyzed", "store": "true"},
                                "delay": {"type": "string", "index": "not_analyzed", "store": "true"},
                                }
                            },
                        }
                    }
                }
            }
        self.update_template = {
            self.type_name: {
                "properties": {
                    "delay_top": {"type": "float", "index": "not_analyzed", "store": "true"},
                }
            }
        }

    def get_record(
            self, index,
            appid,
            userid,
            starttime,
            stoptime,
            ):
        index = index.lower()
        req_dsl = {
                "size": ESSIZEMAX,
                "query": {
                    "bool": {
                        "filter": [
                                {"range": {
                                    "timestamp": {
                                        "gte": starttime.strftime("%Y-%m-%d %H:%M:%S"),
                                        "lte": stoptime.strftime("%Y-%m-%d %H:%M:%S")
                                        }
                                    }
                                },
                            ],
                        "must": [
                            # {"term": {"device_id": device_id}},
                            # {"term": {"target_ip": target_ip}},
                            {"term": {"app_id": appid}},
                            {"term": {"user_id": userid}},
                            ]
                        }
                    }
                }
        req_data = self.es_con.search(index=index, doc_type=self.type_name, body=req_dsl, params={"request_timeout":TIMEOUT})
        return {"checktimes": [item["_source"]["timestamp"]
            for item in req_data["hits"]["hits"]
            ]}

    def get_detail_record(
            self, index,
            appid,
            userid,
            checktime,
            ):
        # index = index.lower()
        index = "{}*".format(index.lower())
        req_dsl = {
                "size": ESSIZEMAX,
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"timestamp": checktime.strftime("%Y-%m-%d %H:%M:%S")}},
                            # {"term": {"device_id": device_id}},
                            # {"term": {"target_ip": target_ip}},
                            {"term": {"app_id": appid}},
                            {"term": {"user_id": userid}},
                            ]
                        }
                    }
                }
        req_data = self.es_con.search(index=index, doc_type=self.type_name, body=req_dsl, params={"request_timeout":TIMEOUT})
        if not req_data["hits"]["hits"]:
            return {"instance": "null"}
        key_list = [
                "channel", "device_id", "target_ip", "remote_ip", "location", "net_type", "net_delay", "device_type",
                "device_name", "device_version",
                "wifi_count", "wifi_rssi", "wifi_channel", "frequency", "speed", "route_delay", "local_delay",
                "cell_rssi", "cell_delay", "traceroute",
                ]
#         return {"instance": {
            # k: v for k, v in req_data["hits"]["hits"][0]["_source"].iteritems() if k in key_list}
#             }
        instance = {}
        for key in key_list:
            if req_data["hits"]["hits"][0]["_source"].has_key(key):
                instance[key] = req_data["hits"]["hits"][0]["_source"][key]
            else:
                instance[key] = None
        return {"instance": instance}

    def get_all_record(
            self, index,
            starttime,
            stoptime,
    ):
        # index = index.lower()
        index = "{}*".format(index.lower())
        req_dsl = {
                "size": ESSIZEMAX,
                "_source": {
                    "include": ["traceroute", "delay_top"]
                    },
                "query": {
                    "bool": {
                        "filter": {
                            "range": {
                                "timestamp": {
                                    "gte": starttime.strftime("%Y-%m-%d %H:%M:%S"),
                                    "lte": stoptime.strftime("%Y-%m-%d %H:%M:%S")
                                    }
                                }
                            }
                        }
                    }
                }
        req_data = self.es_con.search(index=index, doc_type=self.type_name, body=req_dsl, params={"request_timeout":TIMEOUT})
        return [{"traceroute": item["_source"]["traceroute"],
                 "delay_top": item["_source"]["delay_top"],}
                for item in req_data["hits"]["hits"]
                ]



es_trace = ESTrace()
es_heart = ESHeartbeat()
es_query = ESUserQuery()
es_account = ESAccount()