
from . import api
from flask import request
from flask_restful import Resource
from ..models import Group
from ..utils import json_loads
from .. import db


class GroupsList(Resource):
    def get(self):
        args = {k: json_loads(v) for k, v in request.args.to_dict().items()
                if v not in ['']}
        groups = Group.query\
            .filter_by(**{k: v for k, v in args.items() if hasattr(Group, k)})\
            .order_by(Group.name).all()
        return {'groups': [group.to_dict(**args)
                           for group in groups]}

api.add_resource(GroupsList, '/groups')


class Groups(Resource):
    def get(self, group_id):
        group = Group.query.filter_by(id=group_id).first()
        return {'groups': group.to_dict(channels=True)}

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
