import os
import datetime
import shutil
from flask import (render_template, Response, request, current_app,
                   flash, redirect, url_for, send_file, jsonify)
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import main
from .. import db
from ..models import Channel, Group, Origin
from ..api.channels import ChannelsList
from ..utils import json_loads
from ..decorators import admin_required


@main.route('/', methods=['GET'])
def index():
    return redirect(url_for('main.epg'))


@main.route('/login', methods=['GET'])
def login():
    return redirect(url_for('auth.login'))


@main.route('/', methods=['GET'])
@main.route('/management', methods=['GET'])
@login_required
@admin_required
def management():
    return render_template('management/management.html', current_app=current_app)


@main.route('/epg', methods=['GET'])
@login_required
def epg():
    return render_template('epg/epg.html')


@main.route('/download', methods=['GET'])
def download():
    pass


@main.route('/playlist', methods=['GET'])
@login_required
def playlist():
    m3u = []
    m3u.append('#EXTM3U')
    for channel in ChannelsList.get_query().all():
        m3u.append('#EXTINF:-1 group-title="%s" tvg-logo="%s", %s' % (
            channel.group_name, channel.logo, channel.name))
        url = [
            'http://{host}:{port}/channel/{channel_id}'.format(
                host = request.args.get('client_host', '127.0.0.1'),
                port = request.args.get('client_port', 8899),
                channel_id = channel.id
            )]
        m3u.append('&'.join(url))
    return Response('\n'.join(m3u), status=200, mimetype='text/plain')
