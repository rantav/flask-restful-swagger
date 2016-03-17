# -*- coding: utf-8 -*-

from tests.utils import BaseIntegrationTest
from tests.apps.basic_app import app

__author__ = 'sobolevn'


class TestIntegration(BaseIntegrationTest):
    app = app
    base_static_path = '/api/spec/_/static'

    def _assert_request_success(self, response, code=200,
                                content_type='application/json'):
        assert response.status_code == code
        assert response.headers['Content-Type'] == content_type

    def test_basic_integration(self):
        response = self.get('app/registry')
        self._assert_request_success(response)

    def test_basic_integration_json(self):
        response = self.get_raw_link('/api/spec.json')
        self._assert_request_success(response)

    def test_basic_integration_html(self):
        response = self.get_raw_link('/api/spec.html')
        self._assert_request_success(
                response, content_type='text/html; charset=utf-8')

    def test_basic_integration_resource_lister(self):
        response = self.get_raw_link('/api/spec/_/resource_list.json')
        self._assert_request_success(response)

    def test_static_integration_js(self):
        js_files = [
            'lib/shred/content.js',

            'lib/backbone-min.js',
            'lib/handlebars-1.0.0.js',
            'lib/highlight.7.3.pack.js',
            'lib/jquery.ba-bbq.min.js',
            'lib/jquery.slideto.min.js',
            'lib/jquery.wiggle.min.js',
            'lib/jquery-1.8.0.min.js',
            'lib/shred.bundle.js',
            'lib/swagger.js',
            'lib/swagger-oauth.js',
            'lib/underscore-min.js',

            'swagger-ui.js',
            'swagger-ui.min.js',
        ]

        for js in js_files:
            response = self.get_raw_link('{}/{}'.format(
                    self.base_static_path, js))
            self._assert_request_success(
                    response, content_type='text/javascript; charset=utf-8')

    def test_static_integration_css(self):
        css_files = [
            'highlight.default.css',
            'screen.css',
        ]

        for css in css_files:
            response = self.get_raw_link('{}/css/{}'.format(
                    self.base_static_path, css))
            self._assert_request_success(
                    response, content_type='text/css; charset=utf-8')

