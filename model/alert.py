from __future__ import absolute_import

from sqlalchemy import Column, String 

from wtforms import Form, DateTimeField, StringField
from wtforms.validators import Required, AnyOf, UUID

from utils.uuid_type import uuid_gen, datetime_gen
from model.common import BaseModel, DefaultModel

class MonitorAlertDashGetForm(Form):

    starttime = DateTimeField(validators=[Required()], format='%Y-%m-%d+%H:%M:%S')
    stoptime = DateTimeField(validators=[Required()], format='%Y-%m-%d+%H:%M:%S')
    datatype = StringField(validators=[Required(), AnyOf(['delay', 'loss_rate', 'all'])])
    broadband = StringField(validators=[Required()])
    region = StringField(validators=[Required(), UUID()]) 

class MonitorAlertDashDetailForm(Form):

    starttime = DateTimeField(validators=[Required()], format='%Y-%m-%d+%H:%M:%S')
    stoptime = DateTimeField(validators=[Required()], format='%Y-%m-%d+%H:%M:%S')
    # datatype = StringField(validators=[Required(), AnyOf(['delay', 'loss_rate', 'all'])])
    broadband = StringField(validators=[Required()])
    region = StringField(validators=[Required(), UUID()]) 
    province = StringField(validators=[Required()])

class MonitorAlertLogGetForm(Form):

    starttime = DateTimeField(validators=[Required()], format='%Y-%m-%d+%H:%M:%S')
    stoptime = DateTimeField(validators=[Required()], format='%Y-%m-%d+%H:%M:%S')
    state = StringField(validators=[Required(), AnyOf(['open', 'close', 'confirm', 'all'])])

class MonitorAlertLog(BaseModel, DefaultModel):
    
    __tablename__ = 'monitor_alert_log'
    
    id = Column(String(36), default=uuid_gen, primary_key=True)
    start_time = Column(String(20), default=datetime_gen, nullable=False)
    stop_time = Column(String(20), default=datetime_gen, nullable=False)
    # stop_time = Column(String(20), nullable=True)
    state = Column(String(16), nullable=False)
    trigger = Column(String(36), nullable=False)
    rule_name = Column(String(64), nullable=False)
    region = Column(String(64), nullable=False)
    province = Column(String(64), nullable=False)
    county = Column(String(64), nullable=False)
    broadband = Column(String(32), nullable=False)
    appid = Column(String(64), nullable=False)
    serverip = Column(String(36), nullable=False)
    content = Column(String(64), nullable=False)
    content_detail = Column(String(1024), nullable=False)
    
    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.id)
