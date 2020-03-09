#!/bin/sh
#
# Nikola - firewall log sender (a part of www.turris.cz project)
# Copyright (C) 2013-2020 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
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
set -e

debug=0
random_delay=1

while getopts "nd" opt; do
	case "$opt" in
		d)
			debug=1
			;;
		n)
			random_delay=0
			;;
		*)
			echo "Usage: $0 [-d] [-n]"
			exit 1
			;;
	esac
done

# Reset all arguments
set --

# max record count sent to the server
set "$@" -m 1000
# iptables log file
set "$@" -l "/var/log/iptables"
# log file date format
set "$@" -f "%Y-%m-%dT%H:%M:%S"
# path to logrotate config
set "$@" -r "/etc/logrotate.d/iptables"

[ "$random_delay" = 0 ] && set "$@" -n
[ "$debug" = 1 ] && {
	set "$@" -d
	echo nikola "$@"
}

exec nikola "$@"
