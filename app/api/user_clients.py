
from flask import request
from flask_login import current_user, login_required
from flask_restful import Resource, abort
from . import api
from ..models import UserClients
from .. import db


class UserClientsList(Resource):

    @login_required
    def get(self):
        user_clients = UserClients.query\
            .filter_by(user_id=current_user.id).all()
        return [uc.to_dict() for uc in user_clients] if user_clients else []

    @login_required
    def put(self):
        data = request.get_json()
        client = UserClients(user_id=current_user.id, **data)
        db.session.merge(client)
        db.session.commit()
        return client.to_dict()

    @login_required
    def delete(self):
        data = request.get_json()
        client = UserClients.query.filter_by(user_id=current_user.id, **data).first()
        if client:
            db.session.delete(client)
            db.session.commit()
        return client.to_dict()

api.add_resource(UserClientsList, '/userclients')
