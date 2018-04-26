import os
import json
from flask import current_app

from .. import db


class Group(db.Model):
    __tablename__ = 'groups'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(128), nullable=False, unique=True, index=True)
    disable       = db.Column(db.Boolean, default=False)
    channels      = db.relationship('Channel', order_by='Channel.name',
                                    backref='group', lazy='dynamic')
    user_groups   = db.relationship('UserGroups',
                                    backref='group', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Group, self).__init__(**kwargs)

    def to_dict(self, channels=False, **kwargs):
        group = {
            'id': self.id,
            'name': self.name,
            'disable': self.disable
        }
        if channels:
            group['channels'] = [channel.to_dict(**kwargs)
                                 for channel in self.channels]
        return group

    def __repr__(self):
        return '<Group %r>' % self.name

#db.event.listen(Group.name, 'set', Group.on_changed_name)
