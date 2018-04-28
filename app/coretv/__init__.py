
import os
import re
import json
import time
#import urllib
import requests
import importlib
import inspect
import logging
import traceback
import datetime
from flask import current_app
from bs4 import BeautifulSoup
from app import db
from app.models import Origin, EpgChannel
from app.utils import reformat
from functools import reduce

logger = logging.getLogger('app')


class memorize:
    _cache_instance = None
    _relevance = 60

    def __new__(cls, *args):
        if cls._cache_instance is None:
            cls._cache_instance = object.__new__(cls)
        return cls._cache_instance

    def __init__(self, function):
        self._function = function
        self.cache = {}

    def __get__(self, instance, cls=None):
        self._instance = instance
        return self

    def __call__(self, *args, **kwargs):
        if args not in self.cache \
            or self.cache[args]['time'] + self._relevance <= int(time.time()):
            self.cache[args] = {
                'time': int(time.time()),
                'data': self._function(self._instance, *args, **kwargs)
            }
        return self.cache[args]


class Base(object):
    def __init__(self):
        self.logger = logger
        self.json = json
        self.re = re
        self.reformat = reformat
        self.traceback = traceback
        self.datetime = datetime
        self._cost = 99
        self._timeout = (5, 10)
        self._cookie = None

    @property
    def module(self):
        return self.__module__.split('.')[-1]

    @property
    def now_timestamp(self):
        return time.time()

    @property
    def now_datetime(self):
        return datetime.datetime.now().replace(microsecond=0)

    @property
    def cost(self):
        return int(os.getenv('%s_COST' % self.module.upper(),
            self._cost))

    @property
    def timeout(self):
        return os.getenv('RESOURCE_TIMEOUTS',
            current_app.config.get('RESOURCE_TIMEOUTS',
                self._timeout))

    @property
    def cookie(self):
        return self._cookie


    def _get_soup(self, html):
        return BeautifulSoup(html, 'lxml')

    def _get_origins(self):
        return []

    def _get_stream(self, origin):
        return origin.get('link')

    def _get_epg(self):
        return []


    @staticmethod
    def research(pattern, string, group=1):
        try:
            return re.search(pattern, string, re.I).group(group)
        except Exception:
            return ''

    @staticmethod
    def ungzip(filename):
        with gzip.open(filename, 'rb') as f:
            file_content = f.read()
        return file_content

    @staticmethod
    def urlparse(url):
        return requests.urllib3.util.parse_url(url)


class ResourceBase(Base):
    def __init__(self, **kwargs):
        Base.__init__(self)
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def cookie(self):
        try:
            if self._cookie is None:
                with open(os.path.join(current_app.config.get('TMP_DIR', 'tmp'),
                        '%s.cookie' % self.module), 'r') as cs:
                    self._cookie = requests.utils.cookiejar_from_dict(json.load(cs))
        except Exception:
            pass
        return self._cookie

    @cookie.setter
    def cookie(self, value):
        try:
            if isinstance(value, dict):
                self._cookie = requests.utils.cookiejar_from_dict(value)
            else:
                self._cookie = value
                value = requests.utils.dict_from_cookiejar(value)
            with open(os.path.join(current_app.config.get('TMP_DIR', 'tmp'),
                    '%s.cookie' % self.module), 'w') as cs:
                json.dump(value, cs)
        except:
            pass

    def get_response(self, url, referer=None, **kwargs):
        headers = {
            'User-Agent': 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60',
            'Accept': 'text/html, application/xml, application/xhtml+xml, */*',
            'Accept-Language': 'ru,en;q=0.9',
            'Referer': url,
        }
        if referer: headers['Referer'] = referer
        response = requests.get(url, headers=headers, timeout=self.timeout, **kwargs)
        self.logger.debug(response.url)
        response.encoding = 'utf-8'
        return response

    def get_html(self, url, **kwargs):
        response = self.get_response(url, **kwargs)
        return response.text

    def get_json(self, url, default=None, **kwargs):
        try:
            response = self.get_response(url, **kwargs)
            return response.json()
        except Exception:
            return default

    def get_soup(self, url, **kwargs):
        return self._get_soup(self.get_html(url, **kwargs))

    def date_ranges(self, count):
        now = self.now_datetime
        yield now
        for i in range(1, count + 1):
            yield now + self.datetime.timedelta(days=i)

    def get_origins(self):
        for origin in self._get_origins():
            self.logger.debug(origin)
            if origin.get('link'):
                yield {
                    'resource': self.module,
                    'name': origin['name'],
                    'link': origin['link'],
                    #'logo': origin.get('logo', ''),
                    'cost': self.cost,
                }

    def get_stream(self, origin):
        return self._get_stream(origin)

    def get_epg(self):
        return self._get_epg()


def get_resources(module=None):
    modules = []
    for mod_name in os.listdir(os.path.dirname(__file__)):
        if module and module != mod_name[:-3]: continue
        if not mod_name.startswith('mod_'): continue
        try:
            mod_full_name = '%s.%s' % (__name__, mod_name[:-3])
            mod = importlib.import_module(mod_full_name)
            for m in inspect.getmembers(mod, inspect.isclass):
                if m[1].__module__ == mod_full_name:
                    mod_obj = m[1]()
                    modules.append({
                        'name': mod_name,
                        'full_name': mod_full_name,
                        'cls': m[1],
                        'obj': mod_obj,
                        'cost': mod_obj.cost
                    })
        except Exception:
            tb = traceback.format_exc()
            logger.error('%s\n%s', mod_name, tb.strip())
    return sorted(modules, key=lambda k: k['cost'])

def load_origins(module=None):
    for r in get_resources(module):
        if hasattr(r['cls'], 'url') and r['cls'].url:
            try:
                for origin in r['obj'].get_origins():
                    Origin.create_origin(**origin)
                #db.session.commit()
            except Exception:
                tb = traceback.format_exc()
                logger.error('%s\n%s', r, tb.strip())

def load_epgs(module=None):
    from pprint import pprint
    for r in get_resources(module):
        if hasattr(r['cls'], 'epgurl') and r['cls'].epgurl:
            try:
                for epg in r['obj'].get_epg():
                    EpgChannel.insert_epg_channel(**epg)
                #db.session.commit()
            except Exception:
                tb = traceback.format_exc()
                logger.error('%s\n%s', r, tb.strip())
