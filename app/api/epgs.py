
import datetime
from flask import request, jsonify
from flask_restful import Resource, abort
from flask_login import current_user, login_required
from sqlalchemy import or_, and_
from . import api
from ..models import Channel, EpgChannel, Epg, Group, UserChannels, UserGroups
from ..utils import json_loads
from .. import db
from ..decorators import admin_required


class EpgsList(Resource):

    @login_required
    def get(self):
        query = db.session.query(Channel, UserChannels, Group, UserGroups, Epg)\
            .join(Group, Channel.group_id == Group.id)\
            .outerjoin(UserGroups, and_(Group.id == UserGroups.group_id,
                                        UserGroups.user_id == current_user.id))\
            .outerjoin(UserChannels, and_(Channel.id == UserChannels.channel_id,
                                          UserChannels.user_id == current_user.id))\
            .outerjoin(EpgChannel, Channel.epg_channel_id == EpgChannel.id)\
            .outerjoin(Epg, and_(Epg.epg_channel_id == EpgChannel.id,
                                 and_(Epg.date_start <= db.func.now(),
                                      Epg.date_stop >= db.func.now())))\
            .filter(or_(UserGroups.disable == False, UserGroups.disable == None))
        subchann = db.session.query(Channel.id)\
            .filter(Channel.deleted == False)
        if not current_user.is_administrator():
            subgroup = db.session.query(Group.id)\
                .filter(Group.disable == False)
            subchann = subchann.filter(Channel.disable == False)
            query = query.filter(Group.id.in_(subgroup))
        query = query.filter(Channel.id.in_(subchann))
        query = query.order_by(Channel.name)
        return jsonify(epgs=[{
            'channel': {**c.to_dict(), **(uc.to_dict() if uc else {})},
            'group': {**g.to_dict(), **(ug.to_dict() if ug else {})},
            'epg': e.to_dict() if e else None
        } for c, uc, g, ug, e in query.all()])

api.add_resource(EpgsList, '/epgs')


class Epgs(Resource):

    @login_required
    def get(self, channel_id):
        channel = Channel.query.filter_by(id=channel_id).first()
        if channel:
            limit = json_loads(request.args.get('limit', 1))
            query = db.session.query(Epg)\
                .join(EpgChannel, EpgChannel.id == Epg.epg_channel_id)\
                .filter(EpgChannel.id == channel.epg_channel_id,
                        Epg.date_stop > db.func.now())\
                .order_by(Epg.date_start)\
                .limit(limit if isinstance(limit, int) and limit > 0 else 1)
            return jsonify({
                'channel': channel.to_dict() if channel else None,
                'epg': [epg.to_dict() for epg in query.all()]})
        return abort(400, error='channel not found')

api.add_resource(Epgs, '/epgs/<int:channel_id>')


class UserEpgsList(Resource):

    @staticmethod
    def get_query():
        query = db.session.query(Channel, Epg)\
            .join(Group, Channel.group_id == Group.id)\
            .outerjoin(UserGroups, and_(Group.id == UserGroups.group_id,
                                        UserGroups.user_id == current_user.id))\
            .outerjoin(UserChannels, and_(Channel.id == UserChannels.channel_id,
                                          UserChannels.user_id == current_user.id))\
            .join(EpgChannel, Channel.epg_channel_id == EpgChannel.id)\
            .join(Epg, Epg.epg_channel_id == EpgChannel.id)\
            .filter(Epg.date_stop >= db.func.now())\
            .filter(or_(UserGroups.disable == False, UserGroups.disable == None))
        subchann = db.session.query(Channel.id)\
            .filter(Channel.deleted == False)
        if not current_user.is_administrator():
            subgroup = db.session.query(Group.id)\
                .filter(Group.disable == False)
            subchann = subchann.filter(Channel.disable == False)
            query = query.filter(Group.id.in_(subgroup))
        query = query.filter(Channel.id.in_(subchann))
        query = query.order_by(Channel.name)
        return query

    @login_required
    @admin_required
    def get(self):
        return jsonify(epgs=[{
            'channel': {**c.to_dict(), **(uc.to_dict() if uc else {})},
            'group': {**g.to_dict(), **(ug.to_dict() if ug else {})},
            'epg': e.to_dict() if e else None
        } for c, uc, g, ug, e in self.get_query().all()])

api.add_resource(UserEpgsList, '/userepgs')
