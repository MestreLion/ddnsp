#!/usr/bin/env python3
# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>

"""
Personal DDNS Listener
"""

import argparse
import base64
import http.server
import logging
import os.path
import urllib.parse
import ssl

PORT = 8000
log = logging.getLogger(__name__)


class Server(http.server.BaseHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.qs: dict = {}

    def do_GET(self):
        self.get_qs()
        log.debug("%s %s\n\t%s",
            self.address_string(),
            self.requestline,
            self.headers.as_string().strip().replace('\n', '\n\t'),
        )

        ip = self.get_qs('myip', self.address_string())
        hostname = self.get_qs('hostname')
        user, password = self.get_auth()
        res = update_ip(user=user, password=password, hostname=hostname, ip=ip)

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Connection', 'close')
        self.end_headers()

        self.wfile.write(res.encode().strip() + b'\n')

    def get_qs(self, key='', default=''):
        if not key:
            self.qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            return self.qs
        return self.qs.get(key, [''])[0] or default

    def get_auth(self):
        auth = self.headers.get("Authorization", '').split()
        if not (len(auth) == 2 and auth[0] == 'Basic'):
            return '', ''
        try:
            user, password = base64.b64decode(auth[1]).decode().split(':', 1)
        except ValueError:
            return '', ''
        return user, password

    do_POST = do_GET


def update_ip(user, password, hostname, ip):
    log.info(locals())
    return f"good {ip}"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q', '--quiet',
                       dest='loglevel',
                       const=logging.WARNING,
                       default=logging.INFO,
                       action="store_const",
                       help="Suppress informative messages.")

    group.add_argument('-v', '--verbose',
                       dest='loglevel',
                       const=logging.DEBUG,
                       action="store_const",
                       help="Verbose mode, output extra info.")

    parser.add_argument(nargs='?',
                        dest='port',
                        type=int,
                        default=PORT,
                        help="HTTP port to listen. [Default: %(default)s]")

    args = parser.parse_args(argv)
    args.debug = args.loglevel == logging.DEBUG

    return args


def main(argv=None):
    args = parse_args(argv)
    logging.basicConfig(
        level=args.loglevel,
        format="[%(levelname)-8s] %(asctime)s: %(message)s",  # %(module)s
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log.debug(args)
    here = os.path.abspath(os.path.dirname(__file__))
    httpd = http.server.HTTPServer(('', args.port), Server)
    httpd.socket = ssl.wrap_socket(
        httpd.socket,
        keyfile=os.path.join(here, 'privkey.pem'),
        certfile=os.path.join(here, 'fullchain.pem'),
        server_side=True,
    )
    try:
        log.info("Starting server at port %s", args.port)
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        log.info("Server stopped")


if __name__ == '__main__':
    main()
