# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
"""
Personal DDNS Server
"""

import logging
import pprint
import os

import flask

from . import dao
from . import dns
from . import methods
from . import util as u


__all__ = ['CONFIG_DEFAULTS', 'create_app']

SLUG = __name__  # ddnsp

CONFIG_DEFAULTS = dict(
    DNS_BACKEND = 'bind9',
    DNS_DOMAIN = '',
    DNS_SUBDOMAIN = '',
    DNS_TTL = 0,
    HOSTNAME_MAX_LENGTH = 50,
    USERNAME_MAX_LENGTH = 100,
    PASSWORD_MAX_LENGTH = 100,
    PASSWORD_MIN_LENGTH = 6,
)


def create_app(config=None) -> flask.Flask:
    def ipath(*paths):
        return os.path.join(app.instance_path, *paths)

    # create and configure the app
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=ipath(f'{SLUG}.db'),
        **CONFIG_DEFAULTS,
    )
    logging.basicConfig(
        level=logging.DEBUG if app.debug else logging.INFO,
        format="[%(asctime)s] %(levelname)-8s: %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    if config is None:
        app.logger.info("Using config: %s", ipath(f'{SLUG}.cfg'))
        app.config.from_pyfile(f'{SLUG}.cfg', silent=True)
    else:
        app.config.from_mapping(config)

    app.logger.debug("App config: \n%s", pprint.pformat(app.config, indent=2))
    validate_config(app.config)

    try:
        os.makedirs(app.instance_path, mode=0o700)
    except OSError:
        pass

    dao.init_app(app)
    dns.init_app(app)

    @app.route('/')
    def index():
        return "Welcome to <b>ddnsp</b> - Personal Self-Hosted Dynamic DNS\n"

    @app.route('/nic/update')
    def legacy():
        return flask.redirect(flask.url_for('update'), 301)  # Moved Permanently

    @app.route('/update')
    def update():
        req = flask.request
        auth = req.authorization
        app.logger.debug('%s, %s', auth, req.args)
        params = {
            'username': req.args.get('username', auth.get('username', '')),
            'password': req.args.get('password', auth.get('password', '')),
            'hostname': req.args.get('hostname', ''),
            'ip': req.args.get('myip', req.remote_addr or ''),
        }
        app.logger.info("REQ: %s", u.obfuscate(params))
        res = methods.update_ip(**params)
        app.logger.info("RES: %s", res)
        return res

    return app


def validate_config(config) -> None:
    config['DNS_DOMAIN']    = config['DNS_DOMAIN'].strip('. ')
    config['DNS_SUBDOMAIN'] = config['DNS_SUBDOMAIN'].strip('. ')
    try:
        config['HOSTNAME_MAX_LENGTH'] = int(config['HOSTNAME_MAX_LENGTH'])
        config['DNS_TTL'] = int(config['DNS_TTL'])
    except ValueError:
        raise u.DDNSPError("Error in config file values, check integer keys")
    if not (
        config['DNS_DOMAIN'] and
        config['HOSTNAME_MAX_LENGTH']
    ):
        raise u.DDNSPError("Error in config file values, check required keys")
