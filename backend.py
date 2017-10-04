"""
    service.py
    ~~~~~~~~~~

    Short description.

    :copyright: (c) 2017 by Bogoyavlensky Andrey.
"""
import asyncio
import random

import aiohttp
import async_timeout
from sanic import Sanic
from sanic.response import json

app = Sanic()

# TODO: get key from env
API_KEY = 'AIzaSyDPA9hK9qHu3udlUj5T6PIYTrXVR8p-76I'
BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'


async def fetch(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.json()

@app.route("/")
async def test(request):
    # TODO: get address from request
    address = 'Москва+Ботанический+переулок+5'
    await asyncio.sleep(random.choice([0, 0, 0, 3]))
    url = BASE_URL.format(address, API_KEY)
    async with aiohttp.ClientSession() as session:
        results = await fetch(session, url)
    return json(results)

if __name__ == '__main__':
    # TODO: set port as 80
    app.run(host='0.0.0.0', port=8000)
