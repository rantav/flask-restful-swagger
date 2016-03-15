# -*- coding: utf-8 -*-

import json

from tests.utils import BaseIntegrationTest

from tests.apps.basic_app import api_meta

__author__ = 'sobolevn'


class TestSpecJson(BaseIntegrationTest):
    # TODO:
    # def test_model_information(self):
    #   pass
    
    def test_meta_information(self):
        response = self.get_raw_link('/api/spec.json')
        result = json.loads(response.data)
        print result

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
