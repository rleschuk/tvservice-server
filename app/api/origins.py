
from . import api
from flask_restful import Resource
from flask_login import login_required
from ..models import Origin


class OriginsList(Resource):

    @login_required
    def get(self):
        origins = Origin.query.all()
        return {'origins': [origin.to_dict(channel=True, group=True)
                            for origin in origins]}

api.add_resource(OriginsList, '/origins')


class Origins(Resource):

    @login_required
    def get(self, origin_id):
        origin = Origin.query.filter_by(id=origin_id).first()
        return {'origins': origin.to_dict(channel=True, group=True)}

api.add_resource(Origins, '/origins/<int:origin_id>')
