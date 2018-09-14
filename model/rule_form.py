from __future__ import absolute_import

from wtforms import (
        DateTimeField, StringField, SelectField, IntegerField,
        FieldList, FormField, 
        )
from wtforms import Form
from wtforms.validators import (
        Required, UUID, Length, NumberRange,
        AnyOf, Email
        )

'''
Trigger
'''
class MonitorTriggerForm(Form):

    period = StringField(validators=[Required(),
            AnyOf(['1min', '5min', '10min', '30min', '1h'])], )
    time = StringField(validators=[Required(),
            AnyOf(['1c', '2c', '3c', '4c', '5c', '6c', '7c', '8c', '9c', '10c'])])
    repeat = StringField(validators=[Required(),
            AnyOf(['no_repeat', '5min', '10min', '15min', '30min', '1h', '2h', '3h', '5h', '12h'])])
    compare = StringField(validators=[Required(), AnyOf(['>', '<', '='])])
    threshold = IntegerField(validators=[Required()])
    item_id = StringField(validators=[Required(), UUID()])

'''
Contact and Action
'''
class MonitorContactForm(Form):

    contacter = StringField(validators=[Required()])
    mail = StringField(validators=[Required(), Email()])
    telephone = StringField(validators=[Required(), Length(min=11, max=12)])

'''
Rule
'''
# class MonitorRuleRegionForm(Form):

    # region_id = StringField(validators=[Required(), UUID()])

class MonitorRuleForm(Form):

    name = StringField(validators=[Required()])
    regions = FieldList(StringField(validators=[Required(), UUID()]), min_entries=1)
    triggers = FieldList(FormField(MonitorTriggerForm), min_entries=1)
    actions = FieldList(FormField(MonitorContactForm), min_entries=1)
