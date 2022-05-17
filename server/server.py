# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
"""
Personal DDNS Server
"""

import logging
import os

import flask


log = logging.getLogger(__name__)


def create_app(config=None) -> flask.Flask:
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

    @app.route('/')
    def index():
        return "Welcome to <b>ddnsp</b> - Personal Self-Hosted Dynamic DNS\n"

    @app.route('/nic/update')
    def legacy():
        return flask.redirect(flask.url_for('update'), 301)  # Moved Permanently

    @app.route('/update')
    def update():
        app.logger.debug('%s', flask.request.authorization)
        app.logger.debug('%s', flask.request.args)
        params = {
            'hostname': flask.request.args.get('hostname'),
            'ip': flask.request.args.get('myip', flask.request.remote_addr),
        }
        params.update(flask.request.authorization)

        return update_ip(**params)

    return app


def update_ip(username, password, hostname, ip):
    log.info(locals())
    return f"good {ip}"


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)-8s] %(asctime)s: %(message)s",  # %(module)s
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    create_app().run()
