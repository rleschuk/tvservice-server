
from .. import db
from .user import User


class UserClients(db.Model):
    __tablename__    = 'user_clients'
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    host             = db.Column(db.String(15), primary_key=True)
    port             = db.Column(db.Integer, nullable=False, default=8080)
    name             = db.Column(db.String(64))

    @property
    def client_name(self):
        if not self.name:
            return self.host
        return '%s (%s:%s)' % (self.name, self.host, self.port)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'host': self.host,
            'port': self.port,
            'name': self.client_name
        }

    @staticmethod
    def deploy_clients():
        admin = User.query.filter_by(username='admin').first()
        if admin:
            db.session.merge(UserClients(
                user_id = admin.id,
                host = 'localhost',
                port = 8080,
                name = 'develop/testing'
            ))
        db.session.commit()

    def __repr__(self):
        return "<UserClients '%s:%s'>" % (self.host, self.port)
