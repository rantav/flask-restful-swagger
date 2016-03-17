# -*- coding: utf-8 -*-

import unittest

from flask import url_for

from tests.apps import basic_app

__author__ = 'sobolevn'


class BaseIntegrationTest(unittest.TestCase):
    app = None

    def __init__(self, *args, **kwargs):
        super(BaseIntegrationTest, self).__init__(*args, **kwargs)

    def get_url(self, endpoint, endpoint_kwargs=None):
        if endpoint_kwargs is None:
            endpoint_kwargs = {}

        with self.__class__.app.app_context():
            return url_for(endpoint, **endpoint_kwargs)

    def __execute_request(self, method, **kwargs):
        endpoint = kwargs.pop('endpoint')
        endpoint_kwargs = kwargs.pop('endpoint_kwargs')

        with self.__class__.app.app_context():
            with self.__class__.app.test_client() as c:
                url = self.get_url(endpoint, endpoint_kwargs)
                method = getattr(c, method)
                return method(url, **kwargs)

    # TODO: refactor to accept both endpoints and urls
    def get(self, endpoint, endpoint_kwargs=None,
            headers=None, user=None):
        return self.__execute_request(
            'get',
            endpoint=endpoint,
            endpoint_kwargs=endpoint_kwargs,
            headers=headers,
        )

    def post(self, endpoint, endpoint_kwargs=None,
             data=None, headers=None, user=None):
        return self.__execute_request(
            'post',
            data=data,
            endpoint=endpoint,
            endpoint_kwargs=endpoint_kwargs,
            headers=headers,
            follow_redirects=(user is None),
        )

    # TODO: remove this method in favor to `get()`
    def get_raw_link(self, link, *args, **kwargs):
        with self.__class__.app.app_context():
            with self.__class__.app.test_client() as c:
                return c.get(link, *args, **kwargs)
