"""
    service.py
    ~~~~~~~~~~

    Web service to get data from backend.

    :copyright: (c) 2017 by Andrey Bogoyavlensky.
"""
import os
from timeit import default_timer
from urllib.parse import urlencode

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
    """Counts time of execution wrapped code's block."""
    def __init__(self):
        self.timer = default_timer

    def __enter__(self):
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        self.end = self.timer()
        self.interval = self.end - self.start


def do_request(url, params):
    """Requests data from api by url and params."""
    # Try to get results from cache
    query = urlencode(params)
    results = redis_store.get(query)
    if results:
        return json.loads(results)

    response = requests.get('?'.join([url, query]), timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    results = response.json()
    redis_store.set(query, json.dumps(results), CACHE_EXPIRATION)
    return results


@app.route('/geocode/')
def geocode():
    """Returns geocoding for passed address."""
    address = request.args.get('address', None)
    if not address:
        return jsonify(error_message='Missing address in query params'), 400
    params = {'address': address}

    latest_reason = 'Unknown'
    retry_timeout = MAX_RETRY_TIMEOUT
    while retry_timeout > 0:
        try:
            with Timer() as t:
                results = do_request(url=BACKEND_URL, params=params)
        except (RequestException, Timeout):
            latest_reason = 'Server error or timeout'
        except ValueError:
            latest_reason = 'Response decoded error'
        else:
            return jsonify(**results)
        finally:
            retry_timeout -= t.interval

    return jsonify(
        error_message='Something went wrong. Please try again later',
        latest_reason=latest_reason,
    ), 500
