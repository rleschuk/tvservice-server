import re
from flask import current_app

from .. import db
from ..utils import reformat


class Epg(db.Model):
    __tablename__    = 'epgs'
    epg_channel_id   = db.Column(db.Integer, db.ForeignKey('epg_channels.id'), primary_key=True)
    date_start       = db.Column(db.DateTime(), primary_key=True)
    date_stop        = db.Column(db.DateTime(), index=True)
    title            = db.Column(db.String(512), nullable=False,index=True)
    category         = db.Column(db.String(512))
    description      = db.Column(db.Text())
    _arts            = db.Column(db.Text())

    @property
    def arts(self):
        return self._arts.split(',') if self._arts else []

    @arts.setter
    def arts(self, value):
        self._arts = ','.join(value)

    def __init__(self, epg_channel_id, title=None, category=None, description=None, **kwargs):
        super(Epg, self).__init__(**kwargs)
        self.epg_channel_id = epg_channel_id
        self.title = self.format_title(title)
        current_app.logger.debug('<<< title: %r', self.title)
        self.category = self.format_category(category, title)
        current_app.logger.debug('<<< categ: %r', self.category)
        self.description = self.format_description(description, title)
        current_app.logger.debug('<<< descr: %r', self.description)
        current_app.logger.debug('<<< start: %s', self.date_start)
        current_app.logger.debug('<<<  arts: %s', self.arts)

    def __repr__(self):
        return '<Epg %r>' % self.title

    def to_dict(self):
        return {
            'title': self.title,
            'date_start': self.date_start.timestamp(),
            'date_stop': self.date_stop.timestamp() if self.date_stop else None,
            'category': self.category,
            'description': self.description,
            'arts': self.arts
        }

    @staticmethod
    def format_title(string):
        string = reformat(string, (
            (r'^премьера[.!]\s+', ''),
            (r'\[.*?\]', ''),
            (r'&lowast;', ''),
            (r'\(\d+\+\)', ''),
            (r'[хдмкт]\/[фс]', ''),
            (r'[,.]\s+(\d+\s+сезон|сезон\s+\d+)', ''),
            (r'[,.]\s+(\d+\s+(с|ч|эп))', ''),
            (r'[,.]\s+(\d+-\d+\s+(с|ч|эп))', ''),
            (r'[,.]\s+(\d+\s+и\s+\d+\s+(с|ч|эп))', ''),
            (r'[,.]\s+(\d+-я\s+(серия|часть))', ''),
            (r'[,.]\s+(\d+-я\s+[-и]\s+\d+-я\s+серии)', ''),
            (r'\.+$', ''),
        ), flags=re.I)
        string = re.sub(r'^"(.*)"$', r'\1', string) \
            if not re.match(r'\.\s+', string) \
            else re.sub(r'"', r'', string)
        string = reformat(string, ((r'\s\s+', ' '),))
        return string

    @staticmethod
    def format_category(string, title):
        if 'Х/ф' in title: string = 'Художественный фильм'
        if 'Д/ф' in title: string = 'Документальный фильм'
        if 'Т/с' in title: string = 'Сериал'
        if 'Д/с' in title: string = 'Документальный сериал'
        if 'М/с' in title: string = 'Мультсериал'
        if 'М/ф' in title: string = 'Мультфильм'
        if 'К/ф' in title: string = 'Фильм'
        string = reformat(string, ((r'\s\s+', ' '),)).title()
        return string

    @staticmethod
    def format_description(string, title):
        se = []
        s = re.search(r'([,.] (\d+ cезон|cезон \d+))', title, re.I)
        if s:
            title = title.replace(s.group(1), '')
            se.append(s.group(2))
        e = re.search(r'[,.] (\d+ (с|ч)|\d+-\d+ (с|ч)|\d+ и \d+ (с|ч)|\d+-я (серия|часть)|\d+-я [-и] \d+-я серии)', title)
        if e:
            se.append(e.group(1))
        if se:
            string = ', '.join(se) + '\n' + string
        string = reformat(string, ((r'\s\s+', ' '),))
        return string

    @staticmethod
    def insert_epg(epg_channel_id, date_start=None, **item):
        epg = Epg.query.filter_by(
            epg_channel_id = epg_channel_id,
            date_start = date_start).first()
        if epg:
            if not epg.category and item.get('category'):
                epg.category = item.get('category')
            if not epg.description and item.get('description'):
                epg.description = item.get('description')
            if not epg.arts and item.get('arts'):
                epg.arts = item.get('arts')
        else:
            prev_epg = db.session.query(Epg)\
                .filter(Epg.epg_channel_id == epg_channel_id,
                        Epg.date_start == db.session\
                            .query(db.func.max(Epg.date_start))\
                            .filter(Epg.epg_channel_id == epg_channel_id,
                                    Epg.date_start < date_start)).first()
            if prev_epg and prev_epg.date_stop is None:
                prev_epg.date_stop = date_start
                db.session.add(prev_epg)
            epg = Epg(epg_channel_id, date_start=date_start, **item)
        db.session.add(epg)
        db.session.commit()
