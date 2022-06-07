# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
"""
Business logic methods
"""

import logging
import re

import flask

from . import dns
from . import dao
from . import util as u


log = logging.getLogger(__name__)

HOSTNAME_RE = re.compile(r'[\da-z][-_\da-z]*', re.ASCII)
USERNAME_RE = re.compile(r'[\da-z][-_\da-z]*', re.ASCII)


def update_ip(username, password, hostname, ip) -> str:
    """Main method for updating IP"""
    args = locals().copy()
    config = flask.current_app.config
    log.info(u.obfuscate(args))
    try:
        args = check_args(config, args)
    except u.DDNSPError as e:
        return str(e)

    hostname = args['hostname']
    data = dao.get_host(hostname)
    if data:
        if not check_auth(data, **args):
            return 'badauth'
        dao.update_timestamp(hostname)
    else:
        register(**args)
        return f'good {ip}'

    if ip == data['ip']:
        return f'nochg {ip}'

    try:
        dns.update_ip(hostname, ip)
    except u.DDNSPError as e:
        return 'dnserr'

    return f'good {ip}'


def check_args(config:flask.Config, args:dict) -> dict:
    """Check for required and well-formed arguments"""
    data = args.copy()
    hostname = args.get('hostname', '').split('.', 1)[0].strip()
    username = args.get('username', '').strip()
    password = args.get('password', '').strip()

    if not ((0 < len(hostname) <= config['HOSTNAME_MAX_LENGTH']) and
            HOSTNAME_RE.match(hostname)):
        raise u.DDNSPError("nohost")

    if not ((0 < len(username) <= config['USERNAME_MAX_LENGTH']) and
            USERNAME_RE.match(username)):
        raise u.DDNSPError("badauth")

    if not (config['PASSWORD_MIN_LENGTH'] <= len(password) <=
            config['PASSWORD_MAX_LENGTH']):
        raise u.DDNSPError("badauth")

    if not u.is_ipv4(args['ip']):
        raise u.DDNSPError("badagent")  # no good choices for bad arguments

    data['hostname'] = hostname
    data['username'] = username
    data['password'] = password
    return data


def register(username, password, hostname, ip) -> None:
    """Register a new hostname in Database and DNS"""
    data = locals().copy()
    dns.update_ip(hostname=hostname, ip=ip)
    dao.add_host(**data)


def check_auth(data, **args) -> bool:
    """Check authentication data against supplied args"""
    return True
