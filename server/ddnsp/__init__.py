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

SLUG = __name__  # ddnsp


def create_app(config=None) -> flask.Flask:
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)-8s: %(module)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    def ipath(*paths):
        return os.path.join(app.instance_path, *paths)

    # create and configure the app
    app = flask.Flask(__name__, instance_relative_config=True)
    if not app.debug:
        logging.getLogger().setLevel(logging.INFO)

    app.config.from_mapping(
        DATABASE=ipath(f'{SLUG}.db'),
        DNS_BACKEND='bind9'
    )
    if config is None:
        app.logger.info("Using config: %s", ipath(f'{SLUG}.cfg'))
        app.config.from_pyfile(f'{SLUG}.cfg', silent=True)
    else:
        app.config.from_mapping(config)

    app.logger.debug("App config: \n%s", pprint.pformat(app.config, indent=2))

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
        app.logger.debug('%s, %s', flask.request.authorization, flask.request.args)
        params = {
            'hostname': flask.request.args.get('hostname'),
            'ip': flask.request.args.get('myip', flask.request.remote_addr),
        }
        params.update(flask.request.authorization)
        return methods.update_ip(**params)

    return app
