"""
    service.py
    ~~~~~~~~~~

    Web service to connect with backend via API.

    :copyright: (c) 2017 by Andrey Bogoyavlensky.
"""
import os
import requests
import time

from requests.exceptions import RequestException, Timeout
from flask import Flask, request, jsonify
app = Flask(__name__)

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://backend/')
DEFAULT_TIMEOUT = 0.5
RETRY_ATTEMPTS = 3
MAX_TIMEOUT = 2
ASSUMPTION = 0.25
MAX_RETRY_TIMEOUT = MAX_TIMEOUT - (DEFAULT_TIMEOUT + ASSUMPTION)


class Timer:
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = (self.end - self.start) * 100


@app.route('/geocode/')
def geocode():
    address = request.args.get('address', None)
    if not address:
        return jsonify(error_message='Missing address in query params'), 400
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
            return jsonify(**response.json())
        finally:
            retry_timeout -= t.interval

    return jsonify(
        error_message='Something went wrong. Please try again later'), 500
