"""
    service.py
    ~~~~~~~~~~

    Web service to connect with backend via API.

    :copyright: (c) 2017 by Andrey Bogoyavlensky.
"""
import os
from timeit import default_timer

import requests
from flask import Flask, request, jsonify, json
from flask_redis import FlaskRedis
from requests.exceptions import RequestException, Timeout

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://redis:6379')
redis_store = FlaskRedis(app)

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://backend/')
DEFAULT_TIMEOUT = 0.5
RETRY_ATTEMPTS = 3
MAX_TIMEOUT = 2
ASSUMPTION = 0.05
MAX_RETRY_TIMEOUT = MAX_TIMEOUT - (DEFAULT_TIMEOUT + ASSUMPTION)
CACHE_EXPIRATION = os.environ.get('CACHE_EXPIRATION', 10)


class Timer:
    def __init__(self):
        self.timer = default_timer

    def __enter__(self):
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        self.end = self.timer()
        self.interval = self.end - self.start


@app.route('/geocode/')
def geocode():
    address = request.args.get('address', None)
    if not address:
        return jsonify(error_message='Missing address in query params'), 400

    results = redis_store.get(address)
    if results:
        return jsonify(**json.loads(results))

    url = BACKEND_URL + '?address={}'.format(address)
    retry_timeout = MAX_RETRY_TIMEOUT
    while retry_timeout > 0:
        try:
            with Timer() as t:
                response = requests.get(url, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
        except (RequestException, Timeout):
            pass
        else:
            results = response.json()
            redis_store.set(address, json.dumps(results), CACHE_EXPIRATION)
            return jsonify(**results)
        finally:
            retry_timeout -= t.interval

    return jsonify(
        error_message='Something went wrong. Please try again later'), 500
