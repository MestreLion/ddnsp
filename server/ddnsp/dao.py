# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
"""
Data Access Objects
"""

import sqlite3
import os

import flask


def create_db():
    app: flask.Flask = flask.current_app
    with app.open_resource('schema.sql', 'rt') as f:
        get_db().executescript(f.read())
    app.logger.info("Database Created")


def init_app(app: flask.Flask) -> None:
    app.teardown_appcontext(close_db)
    app.logger.info("Using database: %s", app.config['DATABASE'])
    if not os.path.exists(app.config['DATABASE']):
        with app.app_context():
            create_db()


def get_db() -> sqlite3.Connection:
    if 'db' not in flask.g:
        flask.g.db = sqlite3.connect(
            flask.current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
    return flask.g.db


def close_db(_e=None) -> None:
    db = flask.g.pop('db', None)
    if db is not None:
        db.close()


# -----------------------------------------------------------------------------
def update_timestamp(hostname):
    pass
