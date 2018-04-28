
from . import api
from flask import request
from flask_restful import Resource
from flask_login import login_required, current_user
from ..models import Channel, Group, UserChannels
from ..utils import json_loads, format_data
from .. import db


class ChannelsList(Resource):

    @staticmethod
    def get_query():
        args = format_data(request.args.to_dict())
        if current_user.is_administrator():
            query = db.session.query(Channel)
            query = query.outerjoin(Group, Group.id == Channel.group_id)
            if isinstance(args.get('group_id'), int):
                query = query.filter(Group.id == args['group_id'])
            elif args.get('group_id') == 'null':
                query = query.filter(Channel.group_id == None)
            if isinstance(args.get('deleted'), (int, bool)):
                query = query.filter(Channel.deleted == bool(args['deleted']))
            if isinstance(args.get('disable'), (int, bool)):
                query = query.filter(Channel.disable == bool(args['disable']))
            if isinstance(args.get('group_disable'), (int, bool)):
                query = query.filter(Group.disable == bool(args['group_disable']))
        print(query)
        query = query.order_by(Channel.name)
        return query

    @login_required
    def get(self):
        return {'channels': [
            channel.to_dict(origins=request.args.get('origins', False))
            for channel in self.get_query().all()
        ]}

api.add_resource(ChannelsList, '/channels')


class Channels(Resource):

    @login_required
    def get(self, channel_id):
        channel = Channel.query.filter_by(id=channel_id).first()
        return channel.to_dict(origins=True)

    @login_required
    def post(self, channel_id):
        data = request.get_json()
        channel = Channel.query.filter_by(id=channel_id).first()
        if channel is None:
            return {'error': 'not found'}
        for key, value in data.items():
            if hasattr(channel, key):
                setattr(channel, key, value)
        db.session.add(channel)
        db.session.commit()
        return channel.to_dict()

api.add_resource(Channels, '/channels/<int:channel_id>')
