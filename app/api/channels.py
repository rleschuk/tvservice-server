
from . import api
from flask import request
from flask_restful import Resource
from flask_login import login_required, current_user
from ..models import Channel, Group
from ..utils import json_loads
from .. import db


class ChannelsList(Resource):

    @login_required
    def get(self):
        args = {k: json_loads(v) for k, v in request.args.to_dict().items()
                if v not in [''] and hasattr(Channel, k)}
        if current_user.is_administrator(): orm = Channel
        else: orm = UserChannels
        query = db.session.query(orm)\
            .filter(orm.deleted == args.get('deleted', False))
        if args.get('group_id'):
            query = query.filter(orm.group_id == args.get('group_id'))
        if args.get('disable'):
            query = query.filter(orm.disable == args.get('disable'))
        query = query.join(Group, Group.id == orm.group_id)\
            .filter(Group.disable == False)
        query = query.order_by(Channel.name)
        return {'channels': [channel.to_dict(origins=args.get('origins', False))
                             for channel in query.all()]}

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
