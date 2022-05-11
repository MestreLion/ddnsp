`ddnsp` - Personal self-hosted Dynamic DNS
===========================================

Design
------

- [`dyndns2`](https://help.dyn.com/remote-access-api/) protocol for client IP update,
  a widespread standard created by [Dyn](https://dyn.com/) (formerly _DynDns_),
  supported by third-party clients such as [`ddclient`](https://ddclient.net/) and
  [`inadyn`](https://troglobit.com/projects/inadyn/), and compatible with other
  dynamic DNS providers such as [Google Domains](https://domains.google).

Protocol Documentation:
- [Dyn](https://help.dyn.com/remote-access-api/)
- [Dynu](https://www.dynu.com/DynamicDNS/IP-Update-Protocol)
- [Google](https://support.google.com/domains/answer/6147083?hl=en&ref_topic=9018335)

---

Installing
----------

**Client**:

```sh
bash <(wget -qO- https://github.com/MestreLion/ddnsp/raw/main/install-client.sh)
```

or, if cloning the full repository:

```sh
git clone 'https://github.com/MestreLion/ddnsp'
ddnsp/install-client.sh
```

You may also use any third-party clients compatible with the `dyndns2` protocol:

- [DDClient](https://ddclient.net/)

`/etc/ddclient.conf`:
```ini
protocol=dyndns2
ssl=yes
use=web, web=https://api.ipify.org/
server=YOUR_DDNS_SERVER[:PORT]
login=YOUR_USERNAME
password=YOUR_PASSWORD
YOUR_HOSTNAME
```
In older versions you might also have to change `/etc/default/ddclient`:
```ini
run_daemon="true"
```

- [In-A-Dyn](https://troglobit.com/projects/inadyn/)

`/etc/inadyn.conf`:
```ini
custom ddnsp {
        ddns-server = YOUR_DDNS_SERVER[:PORT]
        ddns-path   = "/nic/update?hostname=%h&myip=%i"
        username    = YOUR_USERNAME
        password    = YOUR_PASSWORD
        hostname    = YOUR_HOSTNAME
}
```
In Debian/Ubuntu, also change `/etc/default/inadyn` to enable the daemon:
```ini
RUN_DAEMON="yes"
```
