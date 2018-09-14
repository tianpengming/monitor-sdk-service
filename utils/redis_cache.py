import redis
from conf import settings

class RedisCache(object):

    def __init__(self):
        conf_info = {
                'host': settings.opt['REDIS']['HOST'],
                'port': settings.opt['REDIS']['PORT'],
                'db': settings.opt['REDIS']['DBNUM'],
                }
        self.connect = redis.Redis(**conf_info)

    def set_data(self, key, value):
        return self.connect.set(key, value)

    def get_data(self, key):
        return self.connect.get(key)

    def del_data(self, key):
        return self.connect.delete(key)
