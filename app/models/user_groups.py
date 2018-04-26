
from .. import db


class UserGroups(db.Model):
    __tablename__       = 'user_groups'
    id                  = db.Column(db.Integer, primary_key=True)
    user_id             = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id            = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    disable             = db.Column(db.Boolean, default=False)
    channels            = db.relationship('UserChannels',
                                          backref='group', lazy='dynamic')
    __table_args__      = (db.UniqueConstraint('user_id', 'group_id', name='_user_group_uc'),)

    def __repr__(self):
        return '<UserGroups %r>' % self.group
