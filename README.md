Personal self-hosting Dynamic DNS
=================================

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
