"""
    tests/conftest.py
    ~~~~~~~~~~~~~~~~~

    Testing confiduration and fixtures.

    :copyright: (c) 2017 by Andrey Bogoyavlensky.
"""

import pytest

from service import app as service_app


@pytest.fixture
def app():
    service_app.testing = True
    return service_app
