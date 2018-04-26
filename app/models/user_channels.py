
from .. import db


class UserChannels(db.Model):
    __tablename__      = 'user_channels'
    user_id            = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    channel_id         = db.Column(db.Integer, db.ForeignKey('channels.id'), primary_key=True)
    group_id           = db.Column(db.Integer, db.ForeignKey('user_groups.id'))
    name               = db.Column(db.String(128), nullable=False, unique=True, index=True)
    disable            = db.Column(db.Boolean, default=False)
    deleted            = db.Column(db.Boolean, default=False)

    def to_dict(self, group=False, **kwargs):
        channel = {
            'id': self.id,
            'name': self.name,
            'disable': self.disable,
            'deleted': self.deleted
        }
        if group and self.group:
            channel['group'] = self.group.to_dict(**kwargs)
        return channel

    def __repr__(self):
        return '<UserChannels %r>' % self.name

    @staticmethod
    def update_user_channels(current_user):
        from . import Channel, UserChannels, UserGroups
        user_channels = UserChannels.query\
            .filter_by(user_id=current_user.id).all()
        channels_ids = [c.channel_id for c in user_channels]
        user_groups = UserGroups.query\
            .filter_by(user_id=current_user.id).all()
        groups_ids = [g.group_id for g in user_groups]
        for c in Channel.query.filter(Channel.group_id is not None).all():
            if c.id not in channels_ids:
                if c.group_id not in user_groups:
                    group = UserGroups(
                        user_id = current_user.id,
                        group_id = c.group_id
                    )
                    db.session.add(group)
                    db.session.commit()
                else:
                    group = user_groups[groups_ids.index(c.group_id)]
                db.session.add(UserChannels(
                    user_id = current_user.id,
                    channel_id = c.id,
                    name = c.name,
                    disable = False,
                    deleted = False,
                    group_id = group.id
                ))
                db.session.commit()

    @staticmethod
    def deploy_user_channels():
        pass
