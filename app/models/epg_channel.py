from flask import current_app

from .. import db
from ..utils import md5, normalizing


class EpgChannel(db.Model):
    __tablename__ = 'epg_channels'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(128), nullable=False, unique=True, index=True)
    normalize     = db.Column(db.String(128), nullable=False, index=True)
    channels      = db.relationship('Channel', order_by='Channel.name',
                                    backref='epg_channel', lazy='dynamic')
    epgs          = db.relationship('Epg', order_by='Epg.date_start',
                                    backref='epg_channel', lazy='dynamic')

    def __init__(self, **kwargs):
        super(EpgChannel, self).__init__(**kwargs)
        self.normalize = normalizing(self.name)
        current_app.logger.debug('<<< %r', self.name)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'normalize': self.normalize
        }

    @staticmethod
    def insert_epg_channel(name=None, items=None, **kwargs):
        from . import Epg, Channel, Origin
        normalize = normalizing(name)

        epg_channel = EpgChannel.query.filter_by(normalize=normalize).first()
        if not epg_channel:
            epg_channel = EpgChannel(name=name, **kwargs)
            db.session.add(epg_channel)
            db.session.commit()

        channel = Channel.query.filter_by(normalize=normalize).first()
        if not channel:
            origin = Origin.query.filter_by(normalize=normalize).first()
            if origin:
                channel = origin.channel
        if channel:
            if not channel.epg_channel_id:
                channel.epg_channel_id = epg_channel.id
            db.session.add(channel)
            db.session.commit()

        for item in items:
            Epg.insert_epg(epg_channel.id, **item)

        return epg_channel

    def __repr__(self):
        return '<EpgChannel %r>' % self.name
