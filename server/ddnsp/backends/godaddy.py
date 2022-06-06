# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
"""
GoDaddy DNS API
"""

import logging
import typing as t
import urllib.parse

import requests

from .. import dns
from .. import util as u

log = logging.getLogger(__name__)


class GodaddyAPI(dns.DNSBase):
    HOST:    str   = 'https://api.godaddy.com'
    OTE:     str   = 'https://api.ote-godaddy.com'  # OTE, Operational Test Environment
    PATH:    str   = '/v1/domains'
    TIMEOUT: float = 10

    def __init__(self, **kw):
        super().__init__(**kw)
        self.key:       str = kw.pop('key',       self.config.get("key", ''))
        self.secret:    str = kw.pop('secret',    self.config.get("secret", ''))
        self.shopperid: str = kw.pop('shopperid', self.config.get("shopperid", ''))
        self.ote:      bool = kw.pop('ote',       self.config.get("ote", False))
        self.host:      str = kw.pop('host',      self.config.get("host", self.OTE if self.ote else self.HOST))
        self.path:      str = kw.pop('path',      self.config.get("path", self.PATH))

    @property
    def auth_headers(self) -> dict:
        headers = {'Authorization': f'sso-key {self.key}:{self.secret}'}
        if self.shopperid:
            headers['X-Shopper-Id'] = self.shopperid
        return headers

    @property
    def base_url(self) -> str:
        return urllib.parse.urljoin(self.host, self.path, allow_fragments=False)

    def abs_url(self, *parts:str) -> str:
        base = urllib.parse.urljoin(self.host, self.path, allow_fragments=False)
        for part in filter(None, parts):
            base = '{}/{}'.format(base.rstrip('/'), part.lstrip('/'))
        return base

    def request(
            self,
            method:  str,
            path:    str,
            *,
            query:   dict              = None,
            data:    u.Json            = None,
            timeout: t.Optional[float] = 0,
    ) -> u.Json:
        """
        Raw Godaddy API request
        :param method: HTTP verb: GET, OPTIONS, HEAD, POST, PUT, PATCH, or DELETE
        :param path: URL path to append to <base_url>
        :param query: dict to be encoded as querystring in URL
        :param data: data to be sent as JSON
        :param timeout: in seconds. 0 for default TIMEOUT, None for no timeout.
        :return: object loaded from JSON response
        """
        method = method.upper()
        url = self.abs_url(path)

        headers: dict = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        headers.update(self.auth_headers)

        kwargs: dict = {}
        if query:
            kwargs['query'] = query
        if data:
            kwargs['json'] = data
        if timeout is not None:
            kwargs['timeout'] = timeout or self.TIMEOUT

        log_args = tuple(filter(None, (method, url, query, data)))
        log.debug((len(log_args) * "%s ").strip(), *log_args)

        try:
            response = requests.request(method.upper(), url, headers=headers, **kwargs)
            response.raise_for_status()
        except requests.HTTPError as e:
            raise u.DDNSPRequestError(e.response.text or e,
                                      errno=e.response.status_code,
                                      response=e.response)
        except requests.RequestException as e:
            raise u.DDNSPError(e)

        if not len(response.text.strip()):
            return {}
        return response.json()

    # -------------------------------------------------------------------------
    def get_ips(self, domain:str, name:str, ipv6=False) -> t.List[str]:
        rt = 'AAAA' if ipv6 else 'A'
        res = self.request('GET', '{domain}/records/{rt}/{name}'.format(**locals()))
        return [_['data'] for _ in res]

    def update_ips(self, domain:str, name:str, ips:t.Iterable[str], ttl:int=0, ipv6=False) -> None:
        rt = 'AAAA' if ipv6 else 'A'
        path = '{domain}/records/{rt}/{name}'.format(**locals())
        iplist = list(ips)
        data = []
        for ip in iplist:
            record = {'data': ip}
            if ttl:
                record['ttl'] = ttl
            data.append(record)
        self.log.info("Updating %s.%s: %s",
                      name, domain, iplist if len(iplist) > 1 else iplist[0])
        self.request('PUT', path, data=data)

    def get_ip(self, domain:str, name:str, ipv6=False) -> str:
        res = self.get_ips(**locals())
        return res[0] if res else ''

    def update_ip(self, domain:str, name:str, ip:str, ttl:int=0, ipv6=False) -> None:
        args = locals().copy()
        args['ips'] = [ip]
        del args['ip'], args['self']
        self.update_ips(**args)
