# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
"""
Miscellaneous functions and classes.
"""


class DDNSPError(Exception):
    """Base class for custom exceptions, with errno and %-formatting for args.

    All modules in this package raise this (or a subclass) for all
    explicitly raised, business-logic, expected or handled exceptions
    """
    def __init__(self, msg: object = "", *args, errno: int = 0):
        super().__init__((str(msg) % args) if args else msg)
        self.errno = errno


# noinspection PyPep8Naming
class classproperty:
    def __init__(self, func):
        self.fget = func

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


def obfuscate(d:dict, keys:list=None) -> dict:
    if keys is None:
        keys = ['password']
    return {k: (5 * '*' if k.lower() in keys else v) for k, v in d.items()}
