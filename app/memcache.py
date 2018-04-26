
import time

class timed_memorize(object):
    def __init__(self, function):
        self._relevance = 60
        self._function = function
        self._cache = {}

    def __get__(self, instance, cls):
        self._instance = instance
        return self

    def __call__(self, *args, **kwargs):
        if args not in self._cache \
            or self._cache[args]['time'] + self._relevance <= int(time.time()):
            self._cache[args] = {
                'time': int(time.time()),
                'response': self._function(self._instance, *args, **kwargs)
            }
        return self._cache[args]['response']
