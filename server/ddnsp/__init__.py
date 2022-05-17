# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
"""
Personal DDNS Server
"""

import logging
import os

import flask

from . import dao
from . import methods


log = logging.getLogger(__name__)


def create_app(config=None) -> flask.Flask:
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)-8s: %(message)s",  # %(module)s
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # create and configure the app
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'ddnsp.db'),
    )
    if config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(config)

    try:
        os.makedirs(app.instance_path, mode=0o700)
    except OSError:
        pass

    dao.init_app(app)

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
