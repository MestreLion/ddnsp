# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
"""
Password hashing and related functions
"""

import logging

import argon2
import flask


log = logging.getLogger(__name__)


def get_hasher() -> argon2.PasswordHasher:
    if 'hasher' not in flask.g:
        # For arguments and possible config keys:
        # https://argon2-cffi.readthedocs.io/en/stable/api.html#argon2.PasswordHasher
        # https://argon2-cffi.readthedocs.io/en/stable/parameters.html
        config = flask.current_app.config.get_namespace('ARGON2_')
        flask.g.hasher = argon2.PasswordHasher(**config)
    return flask.g.hasher


def hash_password(password:str) -> str:
    return get_hasher().hash(password)


def verify(hashed:str, plain:str) -> bool:
    try:
        return get_hasher().verify(hashed, plain)
    except argon2.exceptions.VerifyMismatchError:
        # No match, fail silently
        pass
    except argon2.exceptions.VerificationError as e:
        # unknown error in underlying argon2 C lib. Not my fault: WARNING
        log.warning(e)
    except argon2.exceptions.InvalidHash:
        # verify() was given a non-hash, my fault: ERROR
        log.error("Invalid hash: %s", hashed)
    return False


def needs_update(hashed:str) -> bool:
    return get_hasher().check_needs_rehash(hashed)
