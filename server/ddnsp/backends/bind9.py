# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
"""
BIND9 DNS API
"""

from .. import dns


class Bind9API(dns.DNSBase):
    def update_ip(self, hostname, ip):
        self.log.debug("Updating %s to %s", hostname, ip)
