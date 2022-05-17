# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
"""
Personal DDNS Server
"""

import logging

import flask


app = flask.Flask(__name__)
log = logging.getLogger(__name__)


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


def update_ip(username, password, hostname, ip):
    log.info(locals())
    return f"good {ip}"


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)-8s] %(asctime)s: %(message)s",  # %(module)s
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    app.run()
