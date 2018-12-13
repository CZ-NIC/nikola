======
Nikola
======
Simple iptables log collector.
It reads data from /var/log/iptables processes them and sends it to server.
It also performs logrotate to be sure that the same data aren't sent to sever twice.

Installation
============
python setup.py install

example usage of the executable file::

    nikola -l /var/log/iptables -f '%b %d %H:%M:%S'
