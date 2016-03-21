# -*- coding: utf-8 -*-

try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse

from flask import request

from flask_restful_swagger import registry  # this line is temporary required.

__author__ = 'sobolevn'


def get_current_registry(api=None):
    global registry  # TODO: remove globals

    overrides = {}
    if api:
        app_name = api.blueprint.name if api.blueprint else None
    else:
        app_name = request.blueprint
        urlparts = urlparse.urlparse(request.url_root.rstrip('/'))
        proto = request.headers.get("x-forwarded-proto") or urlparts[0]
        overrides = {'basePath': urlparse.urlunparse([proto] + list(urlparts[1:]))}

    if not app_name:
        app_name = 'app'

    overrides['models'] = registry.get('models', {})

    reg = registry.setdefault(app_name, {})
    reg.update(overrides)

    reg['basePath'] = reg['basePath'] + (reg.get('x-api-prefix', '') or '')

    return reg
