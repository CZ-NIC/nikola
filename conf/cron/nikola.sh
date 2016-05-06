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

config_get server_addr server address
config_get max_count server max_count
config_get certificate server certificate
config_get ca_path server ca_path
config_get crl_path server crl_path

config_get log_file logfile path
config_get date_format logfile date_format

config_get log_rotate_conf logrotate path

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

wan="$(get_wans ${wan4} ${wan6})"

optional=""
if [ -n "$max_count" ]; then
	optional="$optional -m '$max_count'"
fi
if [ -n "$log_file" ]; then
	optional="$optional -l '$log_file'"
fi
if [ -n "$date_format" ]; then
	optional="$optional -f '$date_format'"
fi
if [ -n "$log_rotate_conf" ]; then
	optional="$optional -r '$log_rotate_conf'"
fi
if [ -n "$wan" ]; then
	optional="$optional -w $wan"
fi
if [ -n "$certificate" ]; then
	optional="$optional -c $certificate"
fi
if [ -n "$ca_path" ]; then
	optional="$optional -C $ca_path"
fi
if [ -n "$crl_path" ]; then
	optional="$optional -L $crl_path"
fi
if [ "$debug" = 1 ]; then
	optional="$optional -d"
fi
if [ "$random_delay" = 0 ]; then
	optional="$optional -n"
fi
if [ -n "$server_addr" ]; then
	optional="$optional -s \"$server_addr\""
fi

eval nikola "$server_addr" "$optional"
exit $?
