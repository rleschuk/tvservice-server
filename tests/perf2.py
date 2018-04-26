# perf2.py

import requests
import time
from threading import Thread

n = 0

def monitor():
    global n
    while True:
        time.sleep(1)
        print(n, 'reqs/sec')
        n = 0

Thread(target=monitor).start()
while True:
    resp = requests.get('http://192.168.0.2:5000')
    n += 1

