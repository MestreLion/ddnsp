# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
"""
DNS base and backend selector
"""

import importlib
import pkgutil
import typing as t

import flask

from . import util as u


_backends: t.Dict[str,'DNSBase'] = {}
api:       t.Optional['DNSBase'] = None


class DNSBase:
    def __init__(self, app=None):
        app = app or flask.current_app
        prefix = f'DNS_{self.backend.upper()}'
        self.config = {k: v for k, v in app.config.items() if k.startswith(prefix)}
        self.log    = app.logger
        self.log.info("Using DNS backend: %s: %s.%s",
                      self.backend,
                      self.__class__.__module__,
                      self.__class__.__name__)
        self.log.debug("%s config: %s", self.backend, self.config)

    @u.classproperty
    def backend(self) -> str:
        return self.__module__.split('.')[-1]

    def update_ip(self, hostname, ip):
        raise NotImplementedError


def init_app(app:flask.Flask=None, backend:str="") -> DNSBase:
    global _backends
    global api

    if app is None:
        app = flask.current_app

    if not backend:
        backend = app.config['DNS_BACKEND']
    try:
        return _backends[backend]
    except KeyError:
        pass

    from . import backends
    modname = f'{backends.__name__}.{backend}'
    for _, name, _ in pkgutil.iter_modules(backends.__path__):
        if name == backend:
            importlib.import_module(modname)
            break
    else:
        raise u.DDNSPError("DNS backend not found: %s", backend)

    _backends = {cls.backend: cls for cls in DNSBase.__subclasses__()}
    try:
        api = _backends[backend](app=app)
        return api
    except KeyError:
        raise u.DDNSPError("No valid DNS backend for backend: %s", backend)
