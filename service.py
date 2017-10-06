"""
    service.py
    ~~~~~~~~~~

    Web service to get data from backend.

    :copyright: (c) 2017 by Andrey Bogoyavlensky.
"""
from timeit import default_timer
from urllib.parse import urlencode

import requests
from flask import request, jsonify, json, Flask
from requests.exceptions import HTTPError
from requests.exceptions import RequestException, Timeout

import config

# Setup
app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['REDIS_URL'] = config.env('REDIS_URL', default='redis://redis:6379')
config.redis_store.init_app(app)


# Utils

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
    if config.IS_CACHE_ENABLED:
        results = config.redis_store.get(query)
        if results:
            return json.loads(results)

    response = requests.get('?'.join([url, query]),
                            timeout=config.DEFAULT_TIMEOUT)
    response.raise_for_status()
    results = response.json()
    if results.get('status') in config.API_ERRORS:
        raise HTTPError(results.get('error_message', ''))
    if config.IS_CACHE_ENABLED:
        config.redis_store.set(query, json.dumps(results),
                               config.CACHE_EXPIRATION)
    return results


# View

@app.route('/geocode/')
def geocode():
    """Returns geocoding for passed address."""
    address = request.args.get('address', None)
    if not address:
        return jsonify(error_message='Missing address in query params'), 400
    params = {'address': address}

    latest_reason = 'Unknown'
    retry_timeout = config.MAX_RETRY_TIMEOUT
    while retry_timeout > 0:
        try:
            with Timer() as t:
                results = do_request(url=config.BACKEND_URL, params=params)
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
