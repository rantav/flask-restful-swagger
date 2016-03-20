# -*- coding: utf-8 -*-

from tests.utils import BaseIntegrationTest
from tests.apps.basic_app import app

__author__ = 'sobolevn'


class TestHelpPages(BaseIntegrationTest):
    app = app

    html_prefix = '.help.html'
    json_prefix = '.help.json'

    def test_help_pages(self):
        endpoints = [
            '/marshal',
        ]

        for endpoint in endpoints:
            response = self.get_raw_link(endpoint + self.html_prefix)
            self.assert_request_success(
                response, content_type='text/html; charset=utf-8')

            response = self.get_raw_link(endpoint + self.json_prefix)
            self.assert_request_success(response)