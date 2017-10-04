"""
    service.py
    ~~~~~~~~~~

    Web service to connect with backend via API.

    :copyright: (c) 2017 by Andrey Bogoyavlensky.
"""

import os
import requests

from requests.exceptions import RequestException, Timeout
from flask import Flask, request, jsonify
app = Flask(__name__)

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://backend/')
DEFAULT_TIMEOUT = 0.6
RETRY_ATTEMPTS = 3


@app.route('/geocode/')
def hello():
    address = request.args.get('address', None)
    if not address:
        return jsonify(error='Missing address in query params'), 400
    url = BACKEND_URL + '?address={}'.format(address)

    attempts = RETRY_ATTEMPTS
    while attempts:
        try:
            response = requests.get(url, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
        except (RequestException, Timeout):
            attempts -= 1
        else:
            return jsonify(**response.json())

    return jsonify(error='Something goes wrong. Please try again'), 500
