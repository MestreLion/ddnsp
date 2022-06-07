# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
"""
Data Access Objects
"""

import contextlib
import logging
import os
import sqlite3
import typing as t

import flask

log = logging.getLogger(__name__)

Row: 't.TypeAlias' = sqlite3.Row


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
    flask.g.db.row_factory = sqlite3.Row
    return flask.g.db


def close_db(_e=None) -> None:
    db = flask.g.pop('db', None)
    if db is not None:
        db.close()


# -----------------------------------------------------------------------------
def execute(query, args) -> t.Optional[int]:
    """Execute an INSERT, UPDATE or DELETE, return inserted or updated row ID"""
    # using conn's context manager for auto-commit
    with get_db() as conn, contextlib.closing(conn.execute(query, args)) as cur:
        return cur.lastrowid


def fetch(query, args=()) -> t.List[Row]:
    with contextlib.closing(get_db().execute(query, args)) as cur:
        return cur.fetchall()


def fetchone(query, args=()) -> t.Optional[Row]:
    rv = fetch(query, args)
    return rv[0] if rv else None


# -----------------------------------------------------------------------------
def update_timestamp(hostname:str) -> int:
    return execute('UPDATE host'
                   ' SET changed = CURRENT_TIMESTAMP'
                   ' WHERE hostname = ?', [hostname])


def get_host(hostname:str) -> t.Optional[Row]:
    return fetchone('SELECT * FROM host WHERE hostname = ?', [hostname])


def add_host(username, password, hostname, ip) -> int:
    return execute('INSERT INTO host'
                   ' ( username,  password,  hostname,  ip) VALUES'
                   ' (:username, :password, :hostname, :ip)',
                   locals())
