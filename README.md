`ddnsp` - Personal self-hosted Dynamic DNS
===============================================================================
Design
------
- Use [**dyndns2**](https://help.dyn.com/remote-access-api) protocol for client
  IP update, a widespread standard created by _DynDns_ (now [Dyn](https://dyn.com)),
  supported by third-party clients such as [`ddclient`](https://ddclient.net/) and
  [`inadyn`](https://troglobit.com/projects/inadyn/), and compatible with other
  dynamic DNS providers such as [Google Domains](https://domains.google).

- Auto-registration via IP update:
  - If requested hostname is available, register it with the given password
  - Hostnames inactive for a given time are automatically expired and expunged
  - Keep track of hostnames, password and last access time
  - Reject update for an existing hostname if password do not match

- DNS Servers to support:
  - Self-hosted, local [BIND9](https://bind9.net/)
  - [GoDaddy](https://developer.godaddy.com/)
-------------------------------------------------------------------------------
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
script=/update
login=YOUR_USERNAME
password='YOUR_PASSWORD'
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
        ddns-path   = "/update?hostname=%h&myip=%i"
        username    = YOUR_USERNAME
        password    = YOUR_PASSWORD
        hostname    = YOUR_HOSTNAME
}
```
In Debian/Ubuntu, also change `/etc/default/inadyn` to enable the daemon:
```ini
RUN_DAEMON="yes"
```
-------------------------------------------------------------------------------
References
----------
- Other designs
  - [PyDDNS](https://github.com/olimpo88/PyDDNS)
  - [pboehm/ddns](https://github.com/pboehm/ddns)
  - [sftdyn](https://github.com/SFTtech/sftdyn)

- `dyndns2` Protocol Documentation
  - [Dyn](https://help.dyn.com/remote-access-api/)
  - [Dynu](https://www.dynu.com/DynamicDNS/IP-Update-Protocol)
  - [Google](https://support.google.com/domains/answer/6147083?hl=en&ref_topic=9018335)

- GoDaddy DNS API
  - [Domains API](https://developer.godaddy.com/doc/endpoint/domains):
      Official Documentation
  - [mintuhouse/godaddy-api](https://github.com/mintuhouse/godaddy-api):
      Javascript, great Swagger docs
  - [eXamadeus/GoDaddyPy](https://github.com/eXamadeus/godaddypy):
      possibly the most used on PiPy
  - [leonlatsch/godaddy-dyndns](https://github.com/leonlatsch/godaddy-dyndns):
      good KISS reference: single file, < 100 lines
  - [CarlEdman/godaddy-ddns](https://github.com/CarlEdman/godaddy-ddns):
      CLI, and another KISS reference
