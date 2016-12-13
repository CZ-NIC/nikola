#!/bin/sh
#
# Nikola - firewall log sender (a part of www.turris.cz project)
# Copyright (C) 2013 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

. $IPKG_INSTROOT/lib/functions.sh

# run get-api-crl to get the latest CRL
/usr/bin/get-api-crl

config_load nikola

get_wans() {
	# Unify them and remove duplicates
	local list=$(echo "$@" | sed -e 's/  */ /g;s/ /\n/g' | sort -u)
	# return comma-separeted list of wans
	for iface in $list; do
		echo -n "$iface",
	done
}

config_get_bool debug main debug 0
config_get_bool random_delay main random_delay 1

config_get wan4 main wan_ifname
config_get wan6 main wan6_ifname

if [ ! -n "$wan4" ]; then
	# Look into the routing tables to guess WAN4 interfaces
	wan4=$(route -n | sed -ne 's/ *$//;/^0\.0\.0\.0  *[0-9.][0-9.]*  *0\.0\.0\.0/s/.* //p')
fi

if [ ! -n "$wan6" ]; then
	# Look into the routing tables to guess WAN6 interfaces
	wan6=$(route -n -A inet6 | sed -ne 's/ *$//;/^::\/0  /s/.* //p')
fi

if [ " $1" = " -n" ]; then
	force_no_timeout="yes"
fi

wan="$(get_wans ${wan4} ${wan6})"

arguments=""

# server address
arguments="$arguments -s https://api.turris.cz/fw"
# setting the ca path
arguments="$arguments -C /etc/ssl/turris.pem"
# setting the crl path
arguments="$arguments -L /etc/ssl/crl.pem"
# max record count sent to the server
arguments="$arguments -m 1000"
# iptables log file
arguments="$arguments -l /var/log/iptables"
# log file date format
arguments="$arguments -f %Y-%m-%dT%H:%M:%S"
# path to logrotate config
arguments="$arguments -r /etc/logrotate.d/iptables"

if [ -n "$wan" ]; then
	arguments="$arguments -w $wan"
fi
if [ "$random_delay" = 0 -o -n "$force_no_timeout" ]; then
	arguments="$arguments -n"
fi
if [ "$debug" = 1 ]; then
	arguments="$arguments -d"
	echo nikola "$arguments"
fi

eval nikola "$arguments"
exit $?
