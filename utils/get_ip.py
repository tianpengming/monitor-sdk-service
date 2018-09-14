# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import json
import requests
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

check = lambda x: u'未知'.encode() if x=='N/A' else x
cf = lambda x, y: '{0}{1}'.format(x, y) if x!=y and y!='N/A' else check(x)
ip_base = 'http://netbench.ksyun.com/api/data'

def get_ipaddr(ipaddr):
    rep_data = {'type': 'iplib', 'ips': ipaddr}
    resp_data = requests.get(ip_base, rep_data)
    if resp_data.status_code==200:
        try:
            ret_data = json.loads(resp_data.text)
            if ret_data['data'][0]['isp']=='N/A':
                return u'其他'.encode('utf-8')
            else:
                return ret_data['data'][0]['isp']
        except:
            return u'其他'.encode('utf-8')
    else:
        return u'其他'.encode('utf-8')

def get_ipaddr_info(ipaddr):
    rep_data = {'type': 'iplib', 'ips': ipaddr}
    resp_data = requests.get(ip_base, rep_data)
    if resp_data.status_code==200:
        try:
            ret_data = json.loads(resp_data.text)
            if ret_data['status'] == True:
                return {'broadband': check(ret_data['data'][0]['isp']),
                        'country': check(ret_data['data'][0]['country']),
                        'county': cf(ret_data['data'][0]['province'], ret_data['data'][0]['city']),
                        }
        except:
            pass
    return {'broadband': u'未知'.encode(),
            'country': u'未知'.encode(),
            'county': u'未知'.encode(),
            }

def get_ipaddr_list(ip_list):
    rep_data = {'type': 'iplib', 'ips': ','.join(ip_list)}
    resp_data = requests.get(ip_base, rep_data)
    if resp_data.status_code == 200:
        try:
            ret_data = json.loads(resp_data.text)
            if ret_data['status'] == True:
                print ret_data
                return {
                    item['ip']: {
                        'broadband': check(item['isp']),
                        'country': check(item['country']),
                        'county': cf(item['province'], item['city']),
                    }
                    for item in ret_data['data']
                    }
        except:
            pass
    return {
        ip: {
            'broadhand': u'未知'.encode(),
            'country': u'未知'.encode(),
            'county': u'未知'.encode()
        }
        for ip in ip_list
    }
