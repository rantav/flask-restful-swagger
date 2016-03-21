# -*- coding: utf-8 -*-

import os

__version__ = '1.0.0'


class StorageSingleton(object):
    """
    This is a temporary solution, before moving things
    inside the blueprint with all the information inside.
    """
    __obj = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls.__obj is None:
            cls.__obj = object.__new__(cls)

            cls.api_spec_static = ''
            cls.resource_listing_endpoint = None

            cls.registry = {
                'models': {}
            }

            cls.templates = {}

        return cls.__obj

root_path = os.path.dirname(__file__)
