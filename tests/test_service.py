# -*- coding: utf-8 -*-
"""
    test_service.py
    ~~~~~~~~~~~~~~~

    Tests for service app.

    :copyright: (c) 2017 by Andrey Bogoyavlensky.
"""
import json
import time
from urllib.parse import urlencode

import pytest
import requests
import responses
from flask import url_for
from requests import HTTPError, Timeout

import service
from config import BACKEND_URL, redis_store


def test_timer_ok():
    with service.Timer() as t:
        time.sleep(0.2)
    assert 0.2 < t.interval < 0.3


def test_do_request_set_cache_is_ok(client):
    params = {'address': 'test'}
    query = urlencode(params)
    url = BACKEND_URL + '?' + query
    results = {'results': 'test'}
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, body=json.dumps(results), status=200,
                 content_type='application/json')
        assert service.do_request(url, params) == results
        assert len(rsps.calls) == 1
        assert json.loads(redis_store.get(query)) == results
        del redis_store[query]


def test_do_request_get_cache_is_ok(client):
    params = {'address': 'test'}
    query = urlencode(params)
    url = BACKEND_URL + '?' + query
    results = {'results': 'test'}
    assert redis_store.get(query) is None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, body=json.dumps(results), status=200,
                 content_type='application/json')
        service.do_request(url, params)
        assert service.do_request(url, params) == results
        assert len(rsps.calls) == 1
        del redis_store[query]


def test_do_request_catch_query_limit_error(client):
    params = {'address': 'test'}
    query = urlencode(params)
    url = BACKEND_URL + '?' + query
    results = {'status': 'OVER_QUERY_LIMIT', 'error_message': 'error'}
    assert redis_store.get(query) is None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, body=json.dumps(results), status=200,
                 content_type='application/json')
        with pytest.raises(HTTPError):
            service.do_request(url, params)
        assert len(rsps.calls) == 1
        assert redis_store.get(query) is None


def test_geocode_if_not_address_passed_400(client):
    response = client.get(url_for('geocode'))
    assert response.status_code == 400
    assert response.json == {
        'error_message': 'Missing address in query params'}


def test_geocode_ok(client):
    params = {'address': 'test'}
    query = urlencode(params)
    url = BACKEND_URL + '?' + query
    results = {'results': 'test'}
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, body=json.dumps(results), status=200,
                 content_type='application/json')
        response = client.get(url_for('geocode') + '?' + query)
        assert response.status_code == 200
        assert response.json == results
        assert len(rsps.calls) == 1
        del redis_store[query]


def test_geocode_try_to_get_results_insistently_up_to_2_sec(client):
    params = {'address': 'test'}
    query = urlencode(params)
    url = BACKEND_URL + '?' + query
    assert redis_store.get(query) is None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, body=json.dumps({}), status=500,
                 content_type='application/json')
        with service.Timer() as t:
            response = client.get(url_for('geocode') + '?' + query)
        assert t.interval < 2
        assert response.status_code == 500
        assert len(rsps.calls) > 100
        assert redis_store.get(query) is None


def test_geocode_catch_bad_response_value(client, mocker):
    params = {'address': 'test'}
    query = urlencode(params)
    mocker.patch.object(service, 'do_request', side_effect=ValueError)
    response = client.get(url_for('geocode') + '?' + query)
    assert response.status_code == 500
    assert response.json['latest_reason'] == 'Response decoded error'
    assert redis_store.get(query) is None


def test_geocode_catch_timeout_max_up_to_2_sec(client, mocker):
    params = {'address': 'test'}
    query = urlencode(params)
    url = BACKEND_URL + '?' + query
    assert not redis_store.keys()

    def do_timeout(url, params):
        time.sleep(0.4)
        return requests.get(url + '?' + query)

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, body=Timeout(), status=500,
                 content_type='application/json')
        mocker.patch.object(service, 'do_request', side_effect=do_timeout)
        with service.Timer() as t:
            response = client.get(url_for('geocode') + '?' + query)
        assert t.interval < 2
        assert redis_store.get(query) is None
        assert response.status_code == 500
        assert len(rsps.calls) == 4
        assert response.json['latest_reason'] == 'Server error or timeout'


def test_geocode_ok_after_several_errors(client):
    params = {'address': 'test'}
    query = urlencode(params)
    url = BACKEND_URL + '?' + query
    results = {'results': 'test'}
    assert redis_store.get(query) is None
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, body=json.dumps({}), status=500,
                 content_type='application/json')
        rsps.add(responses.GET, url, body=Timeout(), status=500,
                 content_type='application/json')
        rsps.add(responses.GET, url, body=json.dumps({}), status=502,
                 content_type='application/json')
        rsps.add(responses.GET, url, body=json.dumps({}), status=503,
                 content_type='application/json')
        rsps.add(responses.GET, url, body=json.dumps(results), status=200,
                 content_type='application/json')
        with service.Timer() as t:
            response = client.get(url_for('geocode') + '?' + query)
        assert t.interval < 2
        assert response.status_code == 200
        assert response.json == results
        assert len(rsps.calls) == 5
        assert json.loads(redis_store.get(query)) == results
