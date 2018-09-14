from __future__ import absolute_import

from wtforms import (
        DateTimeField, StringField, SelectField, IntegerField,
        FieldList, FormField, 
        )
from wtforms import Form
from wtforms.validators import (
        Required, InputRequired, IPAddress, NumberRange
        )

class MonitorUserQuerySearchForm(Form):

    startpos = IntegerField(validators=[InputRequired()])
    length = IntegerField(validators=[Required(), NumberRange(min=1)])
    userid = StringField(validators=[])
    username = StringField(validators=[])
    servername = StringField(validators=[])

class MonitorUserQueryDetailForm(Form):

    userid = StringField(validators=[])
    # userid = StringField(validators=[Required()])
    # username = StringField(validators=[InputRequired()])
    appid = StringField(validators=[Required()])
    server_name = StringField(validators=[Required()])
    starttime = DateTimeField(validators=[Required()], format='%Y-%m-%d+%H:%M:%S')
    stoptime = DateTimeField(validators=[Required()], format='%Y-%m-%d+%H:%M:%S')

class MonitorHeartbeatForm(Form):

    appid = StringField(validators=[Required()])
    device_id = StringField(validators=[Required()])
    starttime = DateTimeField(validators=[Required()], format='%Y-%m-%d %H:%M:%S')
    duration = IntegerField(validators=[InputRequired()])
    target_ip = StringField(validators=[Required(), IPAddress()])
    user_id = StringField(validators=[Required()])

class MonitorTraceForm(Form):

#     device_id = StringField(validators=[Required()])
#     target_ip = StringField(validators=[Required(), IPAddress()])
    appid = StringField(validators=[Required()])
    userid = StringField(validators=[Required()]) 
    starttime = DateTimeField(validators=[Required()], format='%Y-%m-%d+%H:%M:%S')
    stoptime = DateTimeField(validators=[Required()], format='%Y-%m-%d+%H:%M:%S')

class MonitorTraceDetailForm(Form):

#     device_id = StringField(validators=[Required()])
#     target_ip = StringField(validators=[Required(), IPAddress()])
    appid = StringField(validators=[Required()])
    userid = StringField(validators=[Required()]) 
    checktime = DateTimeField(validators=[Required()], format='%Y-%m-%d %H:%M:%S')

class TraceAllForm(Form):

    starttime = DateTimeField(validators=[Required()], format='%Y-%m-%d+%H:%M:%S')
    stoptime = DateTimeField(validators=[Required()], format='%Y-%m-%d+%H:%M:%S')