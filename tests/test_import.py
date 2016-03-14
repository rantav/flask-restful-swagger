# -*- coding: utf-8 -*-

# from pytest import

__author__ = 'sobolevn'


def assert_each(*args):
    for arg in args:
        assert arg


class TestImports(object):
    def test_import_swagger(self):
        from flask_restful_swagger import swagger
        assert_each(
            swagger,
            swagger.model,
            swagger.operation,
            swagger.nested,
            swagger.nested
        )

    def test_import_docs(self):
        from flask_restful_swagger.swagger import (
            docs, model, operation, nested,
        )
        assert_each(
            docs,
            model,
            operation,
            nested,
        )
