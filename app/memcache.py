
import time

class timed_memorize(object):
    def __init__(self, function, seconds=60):
        self._relevance = seconds
        self._function = function
        self._cache = {}

    def __get__(self, instance, cls):
        self._instance = instance
        return self

    def __call__(self, *args, **kwargs):
        if args not in self._cache \
            or self._cache[args]['time'] + self._relevance <= int(time.time()):
            if hasattr(self, '_instance'):
                response = self._function(self._instance, *args, **kwargs)
            else:
                response = self._function(*args, **kwargs)
            self._cache[args] = {
                'time': int(time.time()),
                'response': response
            }
        return self._cache[args]['response']

def memorize_response(seconds=60):
    def _memorize_response(func):
        return timed_memorize(func, seconds)
    return _memorize_response
