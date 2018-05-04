import os
import json
from flask import current_app, url_for

from .. import db
from ..utils import md5, normalizing


class Channel(db.Model):
    __tablename__    = 'channels'
    id               = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(128), nullable=False, unique=True, index=True)
    normalize        = db.Column(db.String(128), nullable=False, index=True)
    logo             = db.Column(db.String(256))
    disable          = db.Column(db.Boolean, default=False)
    deleted          = db.Column(db.Boolean, default=False)
    group_id         = db.Column(db.Integer, db.ForeignKey('groups.id'))
    epg_channel_id   = db.Column(db.Integer, db.ForeignKey('epg_channels.id'))
    origins          = db.relationship('Origin', order_by='Origin.cost',
                                       backref='channel', lazy='dynamic')
    user_channels    = db.relationship('UserChannels',
                                       backref='channel', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Channel, self).__init__(**kwargs)
        self.normalize = normalizing(self.name)
        if not self.logo:
            self.logo = self.get_logo()

    @property
    def group_name(self):
        return self.group.name if self.group else None

    def to_dict(self, origins=False, group=False, **kwargs):
        channel = {
            'id': self.id,
            'group_id': self.group_id,
            'epg_channel_id': self.epg_channel_id,
            'name': self.name,
            'normalize': self.normalize,
            'logo': self.logo if self.logo else url_for('static',
                filename='images/logos/unknow.png', _external=True),
            'disable': self.disable,
            'deleted': self.deleted,
            'group_name': self.group_name
        }
        if group and self.group:
            channel['group'] = self.group.to_dict(**kwargs)
        if origins:
            channel['origins'] = [origin.to_dict(**kwargs)
                                  for origin in self.origins]
        return channel

    def get_logo(self):
        hash = md5(self.name)
        path = os.path.join(current_app.config['BASE_DIR'],
            'app', 'static', 'images', 'logos', hash)
        for ext in ('png','jpg'):
            if os.path.exists('%s.%s' % (path, ext)):
                return 'images/logos/%s.%s' % (hash, ext)
        if self.logo and 'unknow.png' not in self.logo: return self.logo
        return

    @staticmethod
    def on_changed_name(target, value, oldvalue, initiator):
        target.normalize = normalizing(value)

    @staticmethod
    def deploy_channels():
        with open(os.path.join(current_app.config.get('BASE_DIR'), 'deploy', 'db.json')) as f:
            data = json.load(f)

        from . import Group, Origin
        for g, gv in data.items():
            group = None
            if g:
                group = Group.query.filter_by(name=g).first()
                if group is None:
                    group = Group(**{k:v for k,v in gv.items() if hasattr(Group, k)})
                    db.session.add(group)
                    db.session.commit()
            for c, cv in gv['_channels'].items():
                channel = Channel.query.filter_by(name=cv['name']).first()
                if channel is None:
                    channel = Channel(**{k:v for k,v in cv.items() if hasattr(Channel, k)})
                channel.group_id = group.id if group else None
                channel.logo = channel.get_logo()
                db.session.add(channel)
                db.session.commit()
                for o in cv['_origins']:
                    origin = Origin.query.filter_by(name=o['name'], resource=o['resource']).first()
                    if origin is None:
                        origin = Origin(**{k:v for k,v in o.items() if hasattr(Origin, k)})
                    origin.channel_id = channel.id
                    db.session.add(origin)
                db.session.commit()

    def __repr__(self):
        return '<Channel %r>' % self.name

db.event.listen(Channel.name, 'set', Channel.on_changed_name)
