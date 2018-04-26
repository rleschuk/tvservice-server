import os
import datetime
import shutil
from flask import (render_template, Response, request, current_app,
                   flash, redirect, url_for, send_file)
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import main
from ..models import Channel, Group, Origin
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
    d = datetime.datetime.now()

    ace_host = request.args.get('ace_host')
    #if not ace_host: ace_host = app.settings.get_setting('ace_host')
    ace_port = request.args.get('ace_port')
    #if not ace_port: ace_port = str(app.settings.get_setting('ace_port'))
    hd = json_loads(request.args.get('hd'))
    p2p = json_loads(request.args.get('p2p'))

    #config_ace_host = app.settings.get_setting('ace_host')
    #config_ace_port = str(app.settings.get_setting('ace_port'))

    m3u = []
    m3u.append('#EXTM3U')
    channels = Channel.query.filter_by(disable=False, deleted=False)\
        .join(Group).filter(Group.disable == False)\
        .join(Origin).filter(Channel.origins.any(Origin.disable == False))
    for channel in channels:
        m3u.append('#EXTINF:-1 group-title="%s" tvg-logo="%s", %s' % (
            channel.group.name, channel.logo, channel.name))
        url = [
            'http://{host}:{port}/channels/channel/{hash}'.format(
                host = 'localhost', #app.settings.get_setting('host'),
                port = '8098', #app.settings.get_setting('port'),
                hash = channel.hash
            )]
        #if ace_host != config_ace_host: url.append('ace_host=%s' % ace_host)
        #if ace_port != config_ace_port: url.append('ace_port=%s' % ace_port)
        if isinstance(hd, int): url.append('hd=%s' % hd)
        if isinstance(p2p, int): url.append('p2p=%s' % p2p)
        m3u.append('&'.join(url))
    delta = datetime.datetime.now() - d
    current_app.logger.debug((delta.seconds * 1000 + delta.microseconds / 1000) / 1000.)

    return Response('\n'.join(m3u), status=200, mimetype='text/plain')
