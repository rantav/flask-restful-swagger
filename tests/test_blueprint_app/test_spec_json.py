# -*- coding: utf-8 -*-

import json
import os

from tests.utils import BaseIntegrationTest
from tests.apps.blueprint_app import app

__author__ = 'sobolevn'


class TestBlueprintSpecJson(BaseIntegrationTest):
    app = app

    def _load_spec_json(self, blueprint_path):
        response = self.get_raw_link(blueprint_path + '/api/spec.json')
        return json.loads(response.data)

    def _load_json_fixture(self, filename):
        base = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(base, 'fixtures', 'blueprint_app', filename)
        with open(path) as f:
            return json.load(f)

    def test_full_equality_todo(self):
        fixture = self._load_json_fixture('todo_spec.json')
        real = self._load_spec_json('/api-todo')
        assert fixture == real

    def test_full_equality_marshal(self):
        fixture = self._load_json_fixture('marshal_spec.json')
        real = self._load_spec_json('/api-marshal')
        assert fixture == real
