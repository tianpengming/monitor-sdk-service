import datetime
import requests
import json
import time

delay_sim_list = [
        100.0, 20.0, 70.0, 60.0, 70.0, 40.0, 90.0, 30.0, 20.0, 20.0, 
        100.0, 70.0, 40.0, 100.0, 60.0, 100.0, 80.0, 30.0, 50.0, 20.0
        ]
loss_sim_list = [
        40.0, 40.0, 20.0, 20.0, 60.0, 40.0, 10.0, 100.0, 60.0, 70.0, 
        100.0, 70.0, 40.0, 100.0, 60.0, 100.0, 80.0, 30.0, 50.0, 20.0 
        ]
exp_sim_data = {
        "province": u"\u5171\u4eab\u5730\u5740", "delay": "73.0", "broadband": u"*", u"country": u"\u5171\u4eab\u5730\u5740", 
        "counter": 1, "app_id": u"74ed8706-5d8e-45a6-bab5-9e26109e847e", "devices": 1, "server": u"127.0.0.1", 
        "county": u"*", "max_delay": "100.00", "time": u"2017-08-09 12:03", "loss_rate": "58.36", "type": "network",
        "min_delay": "10.00"
        }
base_url = 'http://127.0.0.1:8888/monitor/alert/'
headers = {'content-type': 'application/json'}
time_sim = datetime.datetime.strptime('2017-08-09 12:03:00', '%Y-%m-%d %H:%M:%S')
now = time_sim

for it in range(20):
    data = exp_sim_data.copy()
    data['delay'] = delay_sim_list[it]
    data['loss_rate'] = loss_sim_list[it]
    now = now + datetime.timedelta(minutes=1)
    data['time'] = now.strftime('%Y-%m-%d %H:%M:%S')
    ret_data = requests.post(base_url, headers=headers, data=json.dumps(data))
    print ret_data
    time.sleep(0.1)
