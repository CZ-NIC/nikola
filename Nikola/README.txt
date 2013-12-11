======
Nikola
======
Simple iptables log collector.
It reads data from /var/log/iptables processes them and sends it to server.
It also performs logrotate to be sure that the same data aren't sent to sever twice.

Requirements
============
* atsha204 (see https://gitlab.labs.nic.cz/router/libatsha204/tree/master/src/python)

Installation
============
python setup.py install

example usage of the executable file::

    nikola http://localhost:8080/ -l /var/log/iptables -f '%b %d %H:%M:%S'
