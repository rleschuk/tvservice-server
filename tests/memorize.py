
from __future__ import print_function

import requests
import time

class singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class memorize(object):
    #__metaclass__ = singleton

    def __init__(self, function, seconds=60):
        self._relevance = seconds
        self._function = function
        self.cache = {}

    def __get__(self, instance, cls):
        self._instance = instance
        return self

    def __call__(self, *args, **kwargs):
        if args not in self.cache \
            or self.cache[args]['time'] + self._relevance <= int(time.time()):
            self.cache[args] = {
                'time': int(time.time()),
                'data': self._function(self._instance, *args, **kwargs)
            }
        print(int(time.time()), self.cache[args])
        return self.cache[args]['data']

def memorize_json(seconds=60):
    def _memorize(func):
        return memorize(func, seconds)
    return _memorize


class Resource:
    url = 'http://pomoyka.lib.emergate.net/trash/ttv-list/ttv.json'

    @memorize_json(300)
    def get_response(self, url):
        response = requests.get(url)
        print(int(time.time()), (response.status_code, response.url))
        return response

    def get_json(self, url, default=None, **kwargs):
        response = self.get_response(url)
        return response.json()

    def get_origins(self):
        return self.get_json(self.url).get('channels', [])


if __name__ == '__main__':
    while True:
        r = Resource()
        o = r.get_origins()
        print(int(time.time()), len(o))
        time.sleep(2)
