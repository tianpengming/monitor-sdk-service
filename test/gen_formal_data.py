# -*- coding:utf-8 -*-

from model.rule import *
from model.common import Session

session = Session()
for item in [
        {'name':u'loss_rate', 'comment':u'网络丢包率'.encode('utf-8'), 'unit':'%'},
        {'name':u'delay', 'comment':u'网络延迟'.encode('utf-8'), 'unit':'ms'}
        ]:
    session.add(MonitorItem(**item))
# session.add(MonitorRegion(name='beijing-1-qu', _serverips=[MonitorServerIp(ip='10.40.44.2')]))
# session.add(MonitorRegion(name='beijing-2-qu', _serverips=[
    # MonitorServerIp(ip='120.1.12.3'),
# #    MonitorServerIp(ip='127.0.0.3'),
# ]))
session.commit()

# item_ids = session.query(MonitorItem).all()
# triggers_list = [
        # {
	    # "period": "1min",
	    # "time": "5c",
	    # "repeat": "1h",
	    # "compare": ">",
	    # "threshold": 90,
	    # "item_id": item_ids[0].id
            # },
        # {
	    # "period": "5min",
	    # "time": "2c",
	    # "repeat": "2h",
	    # "compare": ">",
	    # "threshold": 90,
	    # "item_id": item_ids[1].id
            # }
	# ]
# actions_list = [
        # {
	    # "contacter": "zhangsan",
	    # "mail": "zhenglaobao@163.com",
	    # "telephone": "13412341234"
            # },
        # {
	    # "contacter": "lisi",
	    # "mail": "zhenglaobao@163.com",
	    # "telephone": "13000001111"
            # }
        # ]

# regions = session.query(MonitorRegion).all()
# actions = [MonitorContact(**i) for i in actions_list]
# triggers = [MonitorTrigger(**i) for i in triggers_list]
# session.add(
        # MonitorRule(
            # _actions=actions, _triggers=triggers,
            # name='bj2gaojing', _regions=regions
            # )
        # )
# session.commit()
# for name in ['beijing', 'shanghai', 'tianjin', 'hongkong']:
#     session.add(MonitorRegion(province=name, city=name))
# contact_info = [
        # ('tom', 'tom@kingsoft.com', '13412345678'),
        # ('kitty', 'kitty@kingsoft.com', '13412345787'),
        # ('july', 'july@kingsoft.com', '13412345778'),
#         ]
# for person in contact_info:
    # session.add(MonitorContact(name=person[0], mail=person[1], telephone=person[2]))
# session.commit()

# item_ids = session.query(MonitorItem).all()
# trigger_info = [
    # {'period':5, 'method':'avg', 'compare':'>', 'threshold':20, 'item_id':item_ids[0].id},
    # {'period':5, 'method':'max', 'compare':'>', 'threshold':70, 'item_id':item_ids[1].id},
#     ]
# for item in trigger_info:
    # session.add(MonitorTrigger(**item))
# session.commit()

# region_ids = session.query(MonitorRegion).all()
# contact_ids = session.query(MonitorContact).all()
# action_info = [
        # {'action':'mail', 'contact_id':contact_ids[0].id},
        # {'action':'message', 'contact_id':contact_ids[1].id},
#         ]
# for item in action_info:
    # session.add(MonitorAction(**item))
# session.commit()

# rule_info = [{
            # 'name': 'test', '_triggers': [MonitorTrigger(**i) for i in trigger_info],
            # '_actions': [MonitorAction(**i) for i in action_info], '_regions': region_ids
            # }]
# for item in rule_info:
    # session.add(MonitorRule(**item))
# session.commit()
