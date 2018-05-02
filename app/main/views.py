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
from ..api.channels import UserChannelsList
from ..api.epgs import UserEpgsList
from ..utils import json_loads, xml_text
from ..decorators import admin_required


@main.route('/', methods=['GET'])
@login_required
def index():
    return render_template('epg/epg.html')


@main.route('/epg', methods=['GET'])
@login_required
def epg():
    return render_template('epg/epg.html')


@main.route('/manual', methods=['GET'])
def manual():
    return render_template('manual.html')


@main.route('/management', methods=['GET'])
@login_required
@admin_required
def management():
    return render_template('management/management.html',
                           current_app=current_app)


#@main.route('/download', methods=['GET'])
#def download():
#    pass


@main.route('/playlist', methods=['GET'])
@login_required
def playlist():
    m3u = []
    m3u.append('#EXTM3U')
    for channel, userchannel in UserChannelsList.get_query().all():
        m3u.append('#EXTINF:-1 group-title="%s" tvg-logo="%s", %s' % (
            channel.group_name,
            channel.logo if channel.logo else 'http://%s:%s/static/unknow.png' % \
                (request.args.get('host', '127.0.0.1'), request.args.get('port', 8899)),
            channel.name))
        url = 'http://{host}:{port}/channel/{channel_id}'.format(
                host = request.args.get('host', '127.0.0.1'),
                port = request.args.get('port', 8899),
                channel_id = channel.id)
        m3u.append(url)
    return Response('\n'.join(m3u), status=200, mimetype='text/plain')


@main.route('/epgs', methods=['GET'])
@login_required
def userepgs():
    xml = []
    xml.append('<?xml version="1.0" encoding="utf-8" standalone="yes" ?>')
    xml.append('<tv generator-info-name="TVService">')
    channels = []
    for channel, epg in UserEpgsList.get_query().all():
        if channel.id not in channels:
            channels.append(channel.id)
            xml.append('\n'.join([
                '<channel id="%s">' % channel.id,
                '<display-name lang="ru">%s</display-name>' % xml_text(channel.name),
                '</channel>'
            ]))
        xml.append('\n'.join([
            '<programme start="%s" stop="%s" channel="%s">' % (
                epg.date_start.strftime("%Y%m%d%H%M00 +0300"),
                epg.date_stop.strftime("%Y%m%d%H%M00 +0300"),
                channel.id),
            '<title lang="ru">%s</title>' % xml_text(epg.title),
            '<desc lang="ru">%s</desc>' % xml_text(epg.description),
            '<category lang="ru">%s</category>' % xml_text(epg.category),
            '</programme>'
        ]))
    xml.append('</tv>')
    return Response('\n'.join(xml), status=200, mimetype='text/xml')
