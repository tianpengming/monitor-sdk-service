# -*- coding:utf-8 -*-

from __future__ import absolute_import
import tornado.ioloop
import tornado.web
from tornado.options import options, define

from app import *
from model import create_db, drop_db
from utils import es_client, es_query, es_heart, es_trace, es_account
from conf import settings

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import logging
logger = logging.getLogger()

define('port', default=8888, help='service port', type=int)
define('migration', default='nothing', help='database action', type=str)
define('esindex', default=None, help='elasticsearch index action', type=str)
define('esquery', default=None, help='elasticsearch query index action', type=str)
define('esheart', default=None, help='elasticsearch heart index action', type=str)
define('estrace', default=None, help='elasticsearch trace index action', type=str)
define('esaccount', default=None, help='elasticsearch account index action', type=str)

def migration_handler():
    migrate_dict = {
            'create': create_db,
            'delete': drop_db,
            'nothing': None,
            }
    try:
        func = migrate_dict[options.migration]
        if func is not None:
            func()
            return False
        else:
            return True
    except Exception as e:
        logger.debug(e.message)
        logger.debug('Error: create/delete options supported in [migration]')
    return False

def esindex_handler():
    if options.esindex is not None:
        es = es_client
        esindex = options.esindex
        index_name = 'INDEX'
    elif options.esheart is not None:
        es = es_heart
        esindex = options.esheart
        index_name = 'HEARTINDEX'
    elif options.esquery is not None:
        es = es_query
        esindex = options.esquery
        index_name = 'QUERYINDEX'
    elif options.estrace is not None:
        es = es_trace
        esindex = options.estrace
        index_name = 'TRACEINDEX'
    elif options.esaccount is not None:
        es = es_account
        esindex = options.esaccount
        index_name = 'ACCOUNTINDEX'
    else:
        return True
    try:
        esindex_dict = {
            'create': es.create_index,
            'delete': es.delete_index,
            'update': es.update_index,
            }
        func = esindex_dict[esindex]
        ret = func(settings.opt['ELASTICSEARCH'][index_name])
        if not ret['result']:
            logger.info('Error: create/delete options failed in [esindex/esquery/esheart/estrace/esaccount]')
            logger.info('Message: {}'.format(ret['message']))
        return False
    except Exception as e:
        logger.info(e.message)
        logger.info('Error: create/delete options supported in [esindex/esquery/esheart/estrace/esaccount]')
    return False


if __name__ == "__main__":
    tornado.options.parse_command_line()
    settings.set_logger() 
    if migration_handler() and esindex_handler():
        urls = [
            (r"/monitor/region/", MonitorRegionHandler),
            (r"/monitor/serverip/", MonitorServerIpHandler),
            (r"/monitor/region/serverips/", MonitorRegionServerIpHandler),

            (r"/monitor/item/", MonitorItemHandler),
            (r"/monitor/rule/", MonitorRuleHandler),

            (r"/monitor/alert/", MonitorAlertHandler),
            (r"/monitor/alert/province/", MonitorAlertDashDetailHandler),

            (r"/monitor/rule/log/", MonitorAlertLogHandler),
            (r"/monitor/rule/log/detail/", MonitorAlertLogDetailHandler),
            (r"/monitor/rule/log/make_confirm/", MonitorAlertConfirmHandler),
            
            (r"/monitor/userquery/", MonitorUserQueryHandler),
            (r"/monitor/userquery/detail/", MonitorUserQueryDetailHandler),
            (r"/monitor/userquery/network/", MonitorHeartbeatHandler),
            (r"/monitor/trace/", MonitorTraceHandler),
            (r"/monitor/trace/all/", TraceAllHandler),
            (r"/monitor/trace/detail/", MonitorTraceDetailHandler),
            ]
        application = tornado.web.Application(urls)
        application.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()
