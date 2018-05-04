import os
import re
import json
from datetime import datetime
from flask import current_app

from .. import db
from ..utils import normalizing


class Origin(db.Model):
    __tablename__  = 'origins'
    id             = db.Column(db.Integer, primary_key=True)
    resource       = db.Column(db.String(32), nullable=False, index=True)
    name           = db.Column(db.String(128), nullable=False, index=True)
    normalize      = db.Column(db.String(128), nullable=False, index=True)
    link           = db.Column(db.String(256), nullable=False)
    cost           = db.Column(db.Integer, nullable=False, default=99)
    disable        = db.Column(db.Boolean, default=False)
    deleted        = db.Column(db.Boolean, default=False)
    date_created   = db.Column(db.DateTime(), default=datetime.utcnow)
    date_modified  = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    channel_id     = db.Column(db.Integer, db.ForeignKey('channels.id'))
    __table_args__ = (db.UniqueConstraint('resource', 'name', name='_resource_name_uc'),)

    def __init__(self, **kwargs):
        super(Origin, self).__init__(**kwargs)
        self.normalize = normalizing(self.name)

    def to_dict(self):
        return {
            'id': self.id,
            'resource': self.resource,
            'name': self.name,
            'normalize': self.normalize,
            'link': self.link,
            'cost': self.cost,
            'disable': self.disable,
            'deleted': self.deleted,
            'date_created': self.date_created.__str__(),
            'date_modified': self.date_modified.__str__(),
            'channel_id': self.channel_id
        }

    @staticmethod
    def create_origin(name=None, resource=None, **kwargs):
        origin = Origin.query.filter_by(name=name, resource=resource).first()
        if not origin:
            origin = Origin(name=name, resource=resource, **kwargs)
        else:
            for k, v in kwargs.items():
                if hasattr(origin, k):
                    setattr(origin, k, v)
        db.session.add(origin)
        db.session.commit()

        from . import Channel
        channel = Channel.query.filter_by(normalize=origin.normalize).first()
        if not channel:
            _origin = Origin.query.filter_by(normalize=origin.normalize)\
                .filter(Origin.channel_id is not None).first()
            if _origin:
                origin.channel = _origin.channel
            else:
                channel = Channel(name=name)
                channel.origins.append(origin)
                db.session.add(channel)
        elif not origin.channel:
            origin.channel = channel
        db.session.commit()
        return origin

    def __repr__(self):
        return '<Origin %r>' % self.name
