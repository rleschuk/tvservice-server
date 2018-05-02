
from . import api
from flask import request
from flask_restful import Resource
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from ..models import Group, UserGroups
from ..decorators import admin_required
from ..utils import format_data
from .. import db


class GroupsList(Resource):

    @login_required
    def get(self):
        args = format_data(request.args.to_dict())
        query = db.session.query(Group, UserGroups)\
            .outerjoin(UserGroups, and_(Group.id == UserGroups.group_id,
                                        UserGroups.user_id == current_user.id))
        if not current_user.is_administrator():
            subquery = db.session.query(Group.id).filter(Group.disable == False)
            query = query.filter(Group.id.in_(subquery))
        
        #if isinstance(args.get('disable'), (int, bool)):
        #    query = query.filter(Group.disable == bool(args.get('disable')))\
        #                 .filter(or_(UserGroups.disable == bool(args.get('disable')),
        #                             UserGroups.disable == None))

        query = query.order_by(Group.name)
        return {'groups': [{**g.to_dict(), **(u.to_dict() if u else {})}
                           for g, u in query.all()]}

api.add_resource(GroupsList, '/groups')


class Groups(Resource):

    @login_required
    @admin_required
    def get(self, group_id):
        group = Group.query.filter_by(id=group_id).first()
        return {'groups': group.to_dict(channels=True)}

    @login_required
    @admin_required
    def post(self, group_id):
        data = request.get_json()
        group = Group.query.filter_by(id=group_id).first()
        if group is None:
            return {'error': 'not found'}
        for key, value in data.items():
            if hasattr(group, key):
                setattr(group, key, value)
        db.session.add(group)
        db.session.commit()
        return group.to_dict()

api.add_resource(Groups, '/groups/<int:group_id>')


class UsersGroups(Resource):

    @login_required
    def get(self, group_id):
        group = Group.query.filter_by(id=group_id).first()
        return {'groups': group.to_dict(channels=True)}

    @login_required
    def post(self, group_id):
        data = request.get_json()
        print(data)
        group = UserGroups(user_id=current_user.id,
                           group_id=group_id,
                           disable=bool(data.get('disable')))
        db.session.merge(group)
        db.session.commit()
        return group.to_dict()

api.add_resource(UsersGroups, '/usergroups/<int:group_id>')
