# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
"""
GoDaddy DNS API
"""

from .. import dns


class GodaddyAPI(dns.DNSBase):
    def __init__(self, key:str="", secret:str="", **kwargs):
        super().__init__(**kwargs)
        self.key    = key    or self.config.get("DNS_GODADDY_KEY",    '')
        self.secret = secret or self.config.get("DNS_GODADDY_SECRET", '')

    @property
    def auth_header(self) -> dict:
        return {'Authorization': f'sso-key {self.key}:{self.secret}'}

    def update_ip(self, hostname, ip):
        self.log.debug("Updating %s to %s using %s",
                       hostname, ip, self.auth_header)
