"""
    service.py
    ~~~~~~~~~~

    Short description.

    :copyright: (c) 2017 by Bogoyavlensky Andrey.
"""

from sanic import Sanic
from sanic.response import json

app = Sanic()


@app.route("/")
async def test(request):
    return json({"hello": "world"})

if __name__ == "__main__":
    # TODO: get post and host from env
    app.run(host="0.0.0.0", port=8000)
