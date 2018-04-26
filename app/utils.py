import re
import json
import hashlib
import datetime
from flask import current_app
from functools import reduce

def md5(string):
    return hashlib.md5(string.encode('utf8')).hexdigest()

def reformat(string, patterns=[], flags=0):
    try: return reduce(
        lambda x, kv: re.sub(kv[0], kv[1], x, flags=flags),
        patterns, string).strip()
    except Exception:
        return string.strip()

def normalizing(string):
    return reformat(string,
        current_app.config.get('NORMALIZE_SUBREG', [])).lower()

def json_loads(obj):
    try: return json.loads(obj)
    except Exception: return obj

def format_data(d):
    if isinstance(d, list):
        for i, e in enumerate(d):
            try: d[i] = format_data(e)
            except: pass
    elif isinstance(d, dict):
        for k in d.keys():
            try: d[k] = format_data(d[k])
            except: pass
    elif isinstance(d, str):
        try:
            if '.' in d: d = float(d)
            else: d = int(d)
        except: pass
    elif isinstance(d, datetime.datetime):
        d = d.__str__()
    elif isinstance(d, datetime.timedelta):
        d = d.__str__()
    return d
