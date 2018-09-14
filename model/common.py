from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.orm import sessionmaker
from tornado.options import options, define
from conf import settings

# engine = create_engine('mysql+mysqldb://root@localhost:3306/blog?charset=utf8')
engine = create_engine(
        settings.database_url,
        pool_recycle=settings.opt['DATABASES']['RECONNECTTIME'],
        pool_size=settings.opt['DATABASES']['POOLSIZE'])
BaseModel = declarative_base()
Session = sessionmaker(bind=engine)

class DefaultModel(object):

    __uneditable = []
    
    def __init__(self):
        raise NotImplementedError
   
    def _save(self, session, update=False, commit=True):
        try:
            if not update:
                session.add(self)
        except FlushError:
            # In case of an update operation.
            pass
        if commit:
            session.commit()

    def _delete(self, session, commit=True):
        session.delete(self)
        if commit:
            session.commit()

    def _update_attr(self, **kwargs):
        # data_list = {k: v for k, v in kwargs.iteritems() if k not in self.__class__.__uneditable}
        data_list = {}
        for k, v in kwargs.iteritems():
            if k not in self.__class__.__uneditable:
                data_list[k] = v
        for k, v in data_list.iteritems():
            setattr(self, k, v)

    @classmethod
    def _validate(cls, session, instanceid=None, **kwargs):
        if instanceid is not None:
            instance = session.query(cls).get(instanceid)
            if instance is None:
                return {'instance': None,
                        'message': 'id not exists'}
            else:
                instance._update_attr(**kwargs)
                return {'instance': instance,
                        'message': None}
        else:
            if kwargs.has_key('id'):
                kwargs.pop('id')
            return {'instance': cls(**kwargs), 'message': None}
