
import datetime
from flask import request, jsonify
from flask_restful import Resource, abort
from flask_login import current_user
from . import api
from ..models import Channel, EpgChannel, Epg, Group, UserChannels
from ..utils import json_loads
from .. import db


class EpgsList(Resource):
    def get(self):
        if current_user.is_administrator():
            query = db.session.query(Channel, Epg)\
                .filter(Channel.deleted == False,
                        Channel.epg_channel_id is not None)\
                .join(Group, Channel.group_id == Group.id)\
                .filter(Group.disable == False)\
                .join(EpgChannel, EpgChannel.id == Channel.epg_channel_id)\
                .join(Epg, Epg.epg_channel_id == EpgChannel.id)\
                .filter(Epg.date_start <= datetime.datetime.now(),
                        Epg.date_stop >= datetime.datetime.now())\
                .order_by(Channel.name)
        else:
            query = db.session.query(UserChannels, Epg)\
                .filter(UserChannels.user_id == current_user.id,
                        UserChannels.deleted == False)\
                .join(Channel, UserChannels.channel_id == Channel.id)\
                .filter(Channel.epg_channel_id is not None)\
                .join(Group, UserChannels.group_id == Group.id)\
                .filter(Group.disable == False)\
                .join(EpgChannel, EpgChannel.id == Channel.epg_channel_id)\
                .join(Epg, Epg.epg_channel_id == EpgChannel.id)\
                .filter(Epg.date_start <= datetime.datetime.now(),
                        Epg.date_stop >= datetime.datetime.now())\
                .order_by(UserChannels.name)
        return jsonify(epgs=[{
            'epg': epg.to_dict(),
            'channel': channel.to_dict(group=True),
        } for channel, epg in query.all()])

api.add_resource(EpgsList, '/epgs')


class Epgs(Resource):
    def get(self, channel_id):
        channel = Channel.query.filter_by(id=channel_id).first()
        if channel:
            limit = json_loads(request.args.get('limit', 1))
            query = db.session.query(Epg)\
                .join(EpgChannel, EpgChannel.id == Epg.epg_channel_id)\
                .filter(EpgChannel.id == channel.epg_channel_id,
                        Epg.date_stop > datetime.datetime.now())\
                .order_by(Epg.date_start)\
                .limit(limit if isinstance(limit, int) and limit > 0 else 1)
            return jsonify({
                'channel': channel.to_dict() if channel else None,
                'epg': [epg.to_dict() for epg in query.all()]})
        return abort(400, error='channel not found')

api.add_resource(Epgs, '/epgs/<int:channel_id>')
