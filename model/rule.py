from __future__ import absolute_import

from sqlalchemy import Column, String, Integer, Enum
from sqlalchemy import ForeignKey, Table
from sqlalchemy.orm import relationship

from utils.uuid_type import uuid_gen, datetime_gen
from model.common import BaseModel, DefaultModel
from model.region import MonitorRegion

class MonitorItem(BaseModel, DefaultModel):
    
    __tablename__ = 'monitor_item'
    
    id = Column(String(36), default=uuid_gen, primary_key=True)
    name = Column(String(64), nullable=False)
    comment = Column(String(128), nullable=False)
    unit = Column(String(16), nullable=False)

    def __repr__(self):
        return '{0}({1}:{2})'.format(self.__class__.__name__, self.id, self.name)

'''
Trigger
'''
class MonitorTrigger(BaseModel, DefaultModel):

    __tablename__ = 'monitor_trigger'

    id = Column(String(36), default=uuid_gen, primary_key=True)
    period = Column(String(16), nullable=False)
    time = Column(String(16), nullable=False)
    repeat = Column(String(16), nullable=False)
    compare = Column(Enum('>', '<', '='), nullable=False)
    threshold = Column(Integer, nullable=False)
    update_time = Column(String(20), default=datetime_gen, nullable=False)
    # Many to one - Trigger to Item
    item_id = Column(String(36), ForeignKey('monitor_item.id', ondelete='CASCADE'))
    _item = relationship('MonitorItem', backref='_triggers')
    # Many to one - Trigger to Rule
    _rule_id = Column(String(36), ForeignKey('monitor_rule.id', ondelete='CASCADE'))
    _rule = relationship('MonitorRule', back_populates='_triggers')

    def __repr__(self):
        return '{0}({1}:{2})'.format(self.__class__.__name__, self.id, 'None')

'''
Contact and Action
'''
class MonitorContact(BaseModel, DefaultModel):

    __tablename__ = 'monitor_contact'

    id = Column(String(36), default=uuid_gen, primary_key=True)
    contacter = Column(String(64), nullable=False)
    mail = Column(String(72), nullable=False)
    telephone = Column(String(32), nullable=False)

    # Many to one - Action to Rule
    _rule_id = Column(String(36), ForeignKey('monitor_rule.id', ondelete='CASCADE'))

    def __repr__(self):
        return '{0}({1}:{2})'.format(self.__class__.__name__, self.id, self.name)

# class MonitorAction(BaseModel, DefaultModel):

    # __tablename__ = 'monitor_action'

    # id = Column(String(36), default=uuid_gen, primary_key=True)
    # action = Column(Enum('mail', 'message'), nullable=False)
    # # Many to one - Action to Contact
    # contact_id = Column(String(36), ForeignKey('monitor_contact.id', ondelete='CASCADE'))
    # # Many to one - Action to Rule
    # rule_id = Column(String(36), ForeignKey('monitor_rule.id', ondelete='CASCADE'))

    # def __repr__(self):
        # return '{0}({1}:{2})'.format(self.__class__.__name__, self.id, None)

'''
Rule
'''
rule_region_assoc_table = Table('rule_region_assoc', BaseModel.metadata,
    Column('rule_id', String(36), ForeignKey('monitor_rule.id')),
    Column('region_id', String(36), ForeignKey('monitor_region.id'))
)

class MonitorRule(BaseModel, DefaultModel):

    __tablename__ = 'monitor_rule'

    id = Column(String(36), default=uuid_gen, primary_key=True)
    name = Column(String(64), nullable=False)
    # many to many - Region
    _regions = relationship(
            'MonitorRegion', secondary=rule_region_assoc_table,
            backref='_rules_region' 
            ) 
    # one to many - Rule to Action
    # _actions = relationship('MonitorAction', backref='_rules_action')
    _actions = relationship('MonitorContact', backref='_rule')
    # one to Many - Rule to Trigger
    _triggers = relationship('MonitorTrigger', back_populates='_rule')

    def __repr__(self):
        return '{0}({1}:{2})'.format(self.__class__.__name__, self.id, self.name)

    @staticmethod
    def _validate(session, instanceid=None, **kwargs):
        if kwargs:
            # _actions = [MonitorContact(**item) for item in kwargs['actions']]
            _actions = [MonitorContact(**dict(contacter=item.pop('contacter').encode('utf8'), **item))
                    for item in kwargs['actions']]
            # _triggers = [MonitorTrigger(**dict(item_id=item.pop('item_id'), **item)) for item in kwargs['triggers']]
            _triggers = [MonitorTrigger(**item) for item in kwargs['triggers']]
            _regions = session.query(MonitorRegion).filter(
                   MonitorRegion.id.in_(kwargs['regions'])).all()
            para = {'_actions': _actions, '_triggers': _triggers,
                    'name': kwargs['name'].encode('utf8'), '_regions': _regions}
        if instanceid is not None:
            instance = session.query(MonitorRule).get(instanceid)
            if instance is None:
                return {'instance': None,
                        'message': 'id not exists'}
            else:
                if kwargs:
                    instance._update_attr(**para)
                return {'instance': instance,
                        'message': None}
        else:
            if kwargs:
                return {'instance': MonitorRule(**para), 
                        'message': None}       
            else:
                return {'instance': None,
                        'message': 'parameter not exists when create record'}
