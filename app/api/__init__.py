import json, datetime
from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from flask_login import login_required
from ..utils import format_data
from ..decorators import admin_required


api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

from . import channels
from . import groups
from . import origins
from . import epgs
from . import user_clients

@api_bp.route('/', methods=['GET'])
@login_required
@admin_required
def get_status():
    data = json.dumps(dict(current_app.config), default=format_data)
    return jsonify(json.loads(data))

@api_bp.route('/user', methods=['GET'])
@login_required
@admin_required
def get_user():
    from ..models import User
    from flask_login import current_user
    user = User.query.filter_by(email='demo').first()
    return jsonify(user.to_dict())

from . import errors
