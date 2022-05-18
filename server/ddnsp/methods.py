# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
"""
Business logic methods
"""

import logging

from . import dns
from . import dao
from . import util as u


log = logging.getLogger(__name__)


def update_ip(username, password, hostname, ip):
    """Main method for updating IP"""
    args = locals().copy()
    log.info(u.obfuscate(args))
    res = check_args(**args)
    if res:
        return res

    data = get_entry(hostname)
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
        dns.api.update_ip(hostname, ip)
    except u.DDNSPError as e:
        return 'dnserr'

    return f'good {ip}'


def check_args(**args) -> str:
    """Check for required and well-formed arguments"""
    return ""  # badauth, notfqdn, nohost


def get_entry(hostname) -> dict:
    """Retrieve all info about hostname from database"""
    return {}


def register(username, password, hostname, ip) -> None:
    """Register a new hostname in Database and DNS"""
    dns.api.update_ip(hostname=hostname, ip=ip)
    log.info("Registered new account: %s", u.obfuscate(locals()))


def check_auth(data, **args) -> bool:
    """Check authentication data against supplied args"""
    return True
