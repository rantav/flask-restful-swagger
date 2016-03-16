# -*- coding: utf-8 -*-

"""
Here are the tests to be sure, that basic_app produces the
right swagger's spec-json. It is possible to read the documentation
about swagger 1.1 specification here:
https://groups.google.com/forum/#!topic/swagger-swaggersocket/mHdR9u0utH4

We use fixtures for the tests, because it is human readable, and the result
json can be validated by the swagger itself only since the 1.2
"""

# TODO: validate swagger's spec json with swagger
# itself for the future versions.

import json
import os

from tests.utils import BaseIntegrationTest
from tests.apps.basic_app import api_meta

__author__ = 'sobolevn'


class TestSpecJson(BaseIntegrationTest):
    def _load_spec_json(self):
        response = self.get_raw_link('/api/spec.json')
        return json.loads(response.data)

    def _load_json_fixture(self, filename):
        base = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(base, 'fixtures', 'base_app', filename)
        with open(path) as f:
            return json.load(f)

    def test_full_equality(self):
        fixture = self._load_json_fixture('spec.json')
        real = self._load_spec_json()
        assert fixture == real

    def test_meta_information(self):
        result = self._load_spec_json()

        keys_to_be_equal = [
            'description',
            'apiVersion',
            'produces',
            'resourcePath',
        ]
        for key in keys_to_be_equal:
            assert api_meta[key] == result[key]

        key_mapping = [
            ('api_spec_url', 'spec_endpoint_path'),
        ]
        for meta_key, json_key in key_mapping:
            assert api_meta[meta_key] == result[json_key]
