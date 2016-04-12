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

get_wan() {
	IFACES="$1"
	IGNORE="$2"
	for iface in $IFACES ; do
		if echo "$IGNORE" | grep -qwF "$iface" ; then
			continue;
		fi
		echo "$iface"
		return
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

config_get wan main wan_ifname
config_get wan6 main wan6_ifname

if [ ! -n "$wan" ]; then
	# autodetect using default routes (taken from ucollect init script)

	# Look into the routing tables to guess WAN interfaces
	V4=$(route -n | sed -ne 's/ *$//;/^0\.0\.0\.0  *[0-9.][0-9.]*  *0\.0\.0\.0/s/.* //p')
	V6=$(route -n -A inet6 | sed -ne 's/ *$//;/^::\/0  /s/.* //p')
	# Unify them and remove duplicates
	V4=$(echo "$V4" | sed -e 's/  */ /g;s/ /\n/g' | sort -u)
	V6=$(echo "$V6" | sed -e 's/  */ /g;s/ /\n/g' | sort -u)

	IGNORE=$(uci -X show network | sed -ne 's/^network\.\([^.]*\)=interface$/\1/p' | while read iface ; do
		proto=$(uci -q get network.$iface.proto)
		name=$(echo "$proto-$iface" | head -c 15)
		# TODO: What about L2TP? #3093
		if [ "$proto" = "6in4" -o "$proto" = "6to4" -o "$proto" = "6rd" -o "$proto" = "dslite" ] ; then
			# These are tunnels. We can look into them (and do) and they'll travel through the
			# WAN interface, so we don't need these. Ignore them.
			echo "$name"
		fi
	done)
	wan4=$(get_wan "$V4" "$IGNORE")
	wan6=$(get_wan "$V6" "$IGNORE")
	wan="${wan4},${wan6}"
fi

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
	eval nikola "$server_addr" "$optional"
	exit $?
else
	logger -t nikola -p err "Unable to read the mandatory server address option from the config (/etc/config/nikola). Exitting.."
	exit 1
fi
