import hashlib
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin

from .. import db, login_manager
from . import Role, Permission


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(64), unique=True, index=True)
    username      = db.Column(db.String(64), unique=True, index=True)
    role_id       = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed     = db.Column(db.Boolean, default=False)
    name          = db.Column(db.String(64))
    location      = db.Column(db.String(64))
    member_since  = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen     = db.Column(db.DateTime(), default=datetime.utcnow)
    user_groups   = db.relationship('UserGroups',
                                    backref='user', lazy='dynamic')
    user_channels = db.relationship('UserChannels',
                                    backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN_EMAIL']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #def generate_confirmation_token(self, expiration=3600):
    #    s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #    return s.dumps({'confirm': self.id}).decode('utf-8')

    #def confirm(self, token):
    #    s = Serializer(current_app.config['SECRET_KEY'])
    #    try:
    #        data = s.loads(token.encode('utf-8'))
    #    except:
    #        return False
    #    if data.get('confirm') != self.id:
    #        return False
    #    self.confirmed = True
    #    db.session.add(self)
    #    return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    #def generate_email_change_token(self, new_email, expiration=3600):
    #    s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #    return s.dumps(
    #        {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    #def change_email(self, token):
    #    s = Serializer(current_app.config['SECRET_KEY'])
    #    try:
    #        data = s.loads(token.encode('utf-8'))
    #    except:
    #        return False
    #    if data.get('change_email') != self.id:
    #        return False
    #    new_email = data.get('new_email')
    #    if new_email is None:
    #        return False
    #    if self.query.filter_by(email=new_email).first() is not None:
    #        return False
    #    self.email = new_email
    #    db.session.add(self)
    #    return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def to_dict(self):
        return {
            'user_id': self.id,
            'username': self.username,
            'member_since': self.member_since.__str__(),
            'last_seen': self.last_seen.__str__()
        }

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def deploy_users():
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(
                email = current_app.config['ADMIN_EMAIL'],
                username = 'admin',
                password = 'admin',
                confirmed = True,
                name = 'admin'
            ))
            db.session.commit()

        from . import UserClients
        UserClients.deploy_clients()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
