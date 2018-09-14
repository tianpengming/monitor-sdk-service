from __future__ import absolute_import

from sqlalchemy import Column, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from wtforms import Form, StringField, FieldList
from wtforms.validators import Required, UUID, IPAddress

from utils.uuid_type import uuid_gen
from model.common import BaseModel, DefaultModel
import uuid

class MonitorServerIpForm(Form):

    ip = StringField(validators=[Required(), IPAddress()])

class MonitorServerIp(BaseModel, DefaultModel):

    __tablename__ = 'monitor_serverip'

    id = Column(String(36), default=uuid_gen, primary_key=True)
    ip = Column(String(36), nullable=False, unique=True)

    _region_id = Column(String(36), ForeignKey('monitor_region.id', ondelete='CASCADE'))
    _region = relationship('MonitorRegion', back_populates='_serverips')

    def __repr__(self):
        return '{0}({1}:{2})'.format(self.__class__.__name__, self.id, self.ip)


class MonitorRegionPostForm(Form):

    name = StringField(validators=[Required()])
    # serverips = FieldList(StringField(validators=[UUID()]), min_entries=1)

class MonitorRegionPutForm(Form):

    # name = StringField(validators=[Required()])
    # id = StringField(validators=[Required(), UUID])
    serverips = FieldList(StringField(validators=[UUID()]), min_entries=0)

class MonitorRegion(BaseModel, DefaultModel):

    __tablename__ = 'monitor_region'

    id = Column(String(36), default=uuid_gen, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    
    _serverips = relationship('MonitorServerIp', back_populates='_region')
    
    def __repr__(self):
        return '{0}({1}:{2})'.format(self.__class__.__name__, self.id, self.name)

    @staticmethod
    def _validate(session, instanceid=None, **kwargs):
        if instanceid is not None:
            instance = session.query(MonitorRegion).get(instanceid)
            if instance is None:
                return {'instance': None,
                        'message': 'id not exists'}
            else:
                if kwargs:
                    _serverips = session.query(MonitorServerIp).filter(
                            MonitorServerIp.id.in_(kwargs['serverips'])).all()
                    instance._update_attr(_serverips=_serverips, update=True)
                return {'instance': instance,
                        'message': None}
        else:
#             _serverips = session.query(MonitorServerIp).filter(
#                 MonitorServerIp.id.in_(kwargs['serverips'])).all()
            return {'instance': MonitorRegion(name=kwargs['name'].encode('utf8')), 
                    'message': None}
