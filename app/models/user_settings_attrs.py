
from .. import db

class UserSettingsAttrs(db.Model):
    __tablename__ = 'user_settings_attrs'
    order            = db.Column(db.Integer, primary_key=True)
    name             = db.Column(db.String(64), nullable=False)
    default          = db.Column(db.String(128))
    description      = db.Column(db.Text)
    html             = db.Column(db.Text, nullable=False)
    user_settings    = db.relationship('UserSettings', order_by='UserSettings.attr_id',
                                       backref='attr', lazy='dynamic')

    def to_dict(self):
        return {
            'order': self.order,
            'name': self.name,
            'default': self.default,
            'description': self.description,
            'html': self.html
        }

    @staticmethod
    def insert_settings_attrs():
        db.session.merge(UserSettingsAttrs(
            order = 100,
            name = 'AceStream host',
            default = 'localhost',
            description = '',
            html = '<div>AceStream</div>'
        ))
        db.session.merge(UserSettingsAttrs(
            order = 101,
            name = 'AceStream port',
            default = '6878',
            description = '',
            html = '<div>AceStream</div>'
        ))
        db.session.commit()
