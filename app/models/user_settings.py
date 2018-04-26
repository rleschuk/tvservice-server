
from .. import db
'''
UserSettings = db.Table('user_settings',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('attr_id', db.Integer, db.ForeignKey('user_settings_attrs.order'), primary_key=True),
    db.Column('value', db.String(128))
)
'''
class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    user_id            = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    attr_id            = db.Column(db.Integer, db.ForeignKey('user_settings_attrs.order'), primary_key=True)
    value              = db.Column(db.String(128))

    def to_dict(self):
        return {
            'attr': self.attr.to_dict(),
            'value': self.value
        }
