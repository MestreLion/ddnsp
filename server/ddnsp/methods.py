# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
"""
Business logic methods
"""

import logging


log = logging.getLogger(__name__)


def update_ip(username, password, hostname, ip):
    log.info(locals())
    return f"good {ip}"
