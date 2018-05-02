
from . import api
from flask import request
from flask_restful import Resource
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from ..models import Channel, Group, UserChannels, UserGroups
from ..decorators import admin_required
from ..utils import format_data
from .. import db


class ChannelsList(Resource):

    @login_required
    @admin_required
    def get(self):
        args = format_data(request.args.to_dict())
        query = db.session.query(Channel)\
            .outerjoin(Group, Channel.group_id == Group.id)\

        if isinstance(args.get('group_id'), int):
            query = query.filter(Group.id == args['group_id'])
        elif args.get('group_id') is None:
            query = query.filter(Channel.group_id == None)

        if isinstance(args.get('deleted'), (int, bool)):
            query = query.filter(Channel.deleted == bool(args['deleted']))
        if isinstance(args.get('disable'), (int, bool)):
            query = query.filter(Channel.disable == bool(args['disable']))

        query = query.order_by(Channel.name)
        return {'channels': [
            c.to_dict(origins=request.args.get('origins', False))
            for c in query.all()
        ]}

api.add_resource(ChannelsList, '/channels')


class Channels(Resource):

    @login_required
    @admin_required
    def get(self, channel_id):
        channel = Channel.query.filter_by(id=channel_id).first()
        return channel.to_dict(origins=True)

    @login_required
    @admin_required
    def post(self, channel_id):
        data = request.get_json()
        channel = Channel.query.filter_by(id=channel_id).first()
        if channel is None:
            return {'error': 'not found'}
        if data.get('name'):
            _channel = Channel.query.filter_by(name=data.get('name')).first()
            if _channel:
                for orig in channel.origins:
                    orig.channel_id = _channel.id
                    db.session.add(orig)
                    db.session.commit()
                db.session.delete(channel)
                db.session.commit()
                return _channel.to_dict()
        for key, value in data.items():
            if hasattr(channel, key):
                setattr(channel, key, value)
        db.session.add(channel)
        db.session.commit()
        return channel.to_dict()

api.add_resource(Channels, '/channels/<int:channel_id>')


class UserChannelsList(Resource):

    @staticmethod
    def get_query():
        query = db.session.query(Channel, UserChannels)\
            .join(Group, Channel.group_id == Group.id)\
            .outerjoin(UserGroups, and_(Group.id == UserGroups.group_id,
                                        UserGroups.user_id == current_user.id))\
            .outerjoin(UserChannels, and_(Channel.id == UserChannels.channel_id,
                                          UserChannels.user_id == current_user.id))
        subchann = db.session.query(Channel.id)\
            .filter(Channel.deleted == False)\
            .filter(Channel.disable == False)
        subgroup = db.session.query(Group.id)\
            .filter(Group.disable == False)
        query = query.filter(Group.id.in_(subgroup))\
                     .filter(Channel.id.in_(subchann))
        query = query.filter(or_(UserGroups.disable == False,
                                 UserGroups.disable == None))\
                     .filter(or_(UserChannels.disable == False,
                                 UserChannels.disable == None))
        query = query.order_by(Channel.name)
        return query

    @login_required
    def get(self):
        query = self.get_query()
        return {'channels': [
            {**c.to_dict(), **(uc.to_dict() if uc else {})}
            for c, uc in query.all()
        ]}

api.add_resource(UserChannelsList, '/userchannels')


class UsersChannels(Resource):

    @login_required
    def get(self, channel_id):
        channel = Channel.query.filter_by(id=channel_id).first()
        return channel.to_dict(origins=True)

api.add_resource(UsersChannels, '/userchannels/<int:channel_id>')
