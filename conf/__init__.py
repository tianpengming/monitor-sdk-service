import yaml
import os 
import logging

SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SETTINGS_DIR)

class BaseSetting(object):
   
    def __init__(self, base_dir):
        self.make_default()
        with open(os.path.join(base_dir, "settings.yaml")) as fd:
            self.opt.update(**yaml.load(fd.read()))
        self.make_esindex_name()

    def make_esindex_name(self):
        self.opt['ELASTICSEARCH']['INDEX'] = '{}_{}'.format(self.opt['ELASTICSEARCH']['INDEX'], self.opt['ELASTICSEARCH']['APPID'])
        self.opt['ELASTICSEARCH']['HEARTINDEX'] = '{}_{}'.format(self.opt['ELASTICSEARCH']['HEARTINDEX'], self.opt['ELASTICSEARCH']['APPID'])
        self.opt['ELASTICSEARCH']['QUERYINDEX'] = '{}_{}'.format(self.opt['ELASTICSEARCH']['QUERYINDEX'], self.opt['ELASTICSEARCH']['APPID'])
        self.opt['ELASTICSEARCH']['TRACEINDEX'] = '{}_{}'.format(self.opt['ELASTICSEARCH']['TRACEINDEX'], self.opt['ELASTICSEARCH']['APPID'])
        self.opt['ELASTICSEARCH']['ACCOUNTINDEX'] = '{}_{}'.format(self.opt['ELASTICSEARCH']['ACCOUNTINDEX'], self.opt['ELASTICSEARCH']['APPID'])

    def make_default(self):
        self.opt = {
                'DATABASES': {'ENGINE': 'sqlite', 'NAME': 'sqlite.db'},
                'ELASTICSEARCH': {
                    'HOST': ['localhost'],
                    'PORT': 9200,
                    'INDEX': 'gen',
                    'HEARTINDEX': 'heart',
                    'QUERYINDEX': 'user',
                    'TRACEINDEX': 'trace',
                    'ACCOUNTINDEX': 'account',
                    'APPID': '1111-1111'
                    },
                'REDIS': {'HOST': 'localhost', 'PORT': 6379},
                'RUNLEVEL': 'DEBUG',
                'DEBUG': False,
                }
    
    def set_logger(self):
#         logging.basicConfig(level=getattr(logging, self.opt['RUNLEVEL']),
                # format='[%(asctime)s]-[%(filename)s:%(lineno)d]-[%(levelname)s]: %(message)s',
                # datefmt='%a, '
#                 )
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, self.opt['RUNLEVEL']))

    @property
    def database_url(self):
        if self.opt['DATABASES']['ENGINE'] == 'sqlite':
            return 'sqlite:///{}'.format(
                    self.opt['DATABASES']['NAME']
                    )
        elif self.opt['DATABASES']['ENGINE'] == 'mysql':
            if self.opt['DATABASES'].get('PASSWORD'):
                return 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}'.format(
                    self.opt['DATABASES'].get('USERNAME', 'root'),
                    self.opt['DATABASES']['PASSWORD'],
                    self.opt['DATABASES'].get('HOST', 'localhost'),
                    self.opt['DATABASES'].get('PORT', 3306),
                    self.opt['DATABASES'].get('NAME', 'monitor_service'),
                    self.opt['DATABASES'].get('RECONNECTTIME', 3600),
                    self.opt['DATABASES'].get('POOLSIZE', 100),
                    )
            else:
                return 'mysql+pymysql://{0}:@{1}:{2}/{3}'.format(
                    self.opt['DATABASES'].get('USERNAME', 'root'),
                    self.opt['DATABASES'].get('HOST', 'localhost'),
                    self.opt['DATABASES'].get('PORT', 3306),
                    self.opt['DATABASES'].get('NAME', 'monitor_service'),
                    self.opt['DATABASES'].get('RECONNECTTIME', 3600),
                    self.opt['DATABASES'].get('POOLSIZE', 100),
                    )
        else:
            return 'sqlite:///sqlite.db'

settings = BaseSetting(BASE_DIR)
