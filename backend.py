"""
    backend.py
    ~~~~~~~~~~

    Emulating unstable backend for API.

    :copyright: (c) 2017 by Bogoyavlensky Andrey.
"""
import asyncio
import os
import random

import aiohttp
import async_timeout
from sanic import Sanic
from sanic.response import json, HTTPResponse

app = Sanic()
app.config.LOGO = None

API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
BASE_URL = ('https://maps.googleapis.com/maps/api/geocode/json'
            '?address={}&key={}')
ERROR = 'error'
TIMEOUT = 'timeout'
OK = 'OK'
LAGS = [
    {'name': ERROR, 'values': [500, 502, 503]},
    {'name': TIMEOUT, 'values': [0.5, 1, 2, 3, 5]},
    {'name': OK, 'values': []}
]
WEIGHTS = [0.25, 0.25, 0.5]


async def get_random_lag():
    """Emulate some lag with request to API."""
    results = random.choices(LAGS, weights=WEIGHTS, k=1)
    return results[0] if results else {}


async def fetch(session, url):
    """Requests api by url and returns json from response."""
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.json()


@app.route("/")
async def geocode(request):
    """Returns geocode resulting respons from API."""
    address = request.args.get('address', '')
    if not address:
        return HTTPResponse('Missing address in query params', status=400)
    url = BASE_URL.format(address, API_KEY)

    lag = await get_random_lag()
    if lag.get('name') == TIMEOUT:
        await asyncio.sleep(random.choice(lag['values']))
    elif lag.get('name') == ERROR:
        status = random.choice(lag['values'])
        return HTTPResponse('', status=status)

    async with aiohttp.ClientSession() as session:
        results = await fetch(session, url)
        return json(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, workers=3)
