
from .. import db


class UserGroups(db.Model):
    __tablename__       = 'user_groups'
    user_id             = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    group_id            = db.Column(db.Integer, db.ForeignKey('groups.id'), primary_key=True)
    disable             = db.Column(db.Boolean, default=False)

    @property
    def name(self):
        return self.group.name

    def to_dict(self):
        return {
            'group_id': self.group_id,
            'disable': self.disable,
        }

    def __repr__(self):
        return '<UserGroups %r>' % self.group_id
