
from .. import db


class UserChannels(db.Model):
    __tablename__      = 'user_channels'
    user_id            = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    channel_id         = db.Column(db.Integer, db.ForeignKey('channels.id'), primary_key=True)
    disable            = db.Column(db.Boolean, default=False)
    deleted            = db.Column(db.Boolean, default=False)

    @property
    def name(self):
        return self.channel.name

    def to_dict(self, group=False, **kwargs):
        return {
            'disable': self.disable,
            'deleted': self.deleted
        }

    def __repr__(self):
        return '<UserChannels %r>' % self.name
