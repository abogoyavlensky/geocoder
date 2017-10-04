"""
    service.py
    ~~~~~~~~~~

    Web service to connect with backend via API.

    :copyright: (c) 2017 by Andrey Bogoyavlensky.
"""


from flask import Flask
app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"
