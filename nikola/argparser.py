#
# Nikola - firewall log sender (a part of www.turris.cz project)
# Copyright (C) 2018 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
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


import argparse


def get_arg_parser():
    parser = argparse.ArgumentParser(prog="nikola")
    parser.add_argument(
        "-s", "--socket", dest='socket_path', default='ipc:///tmp/sentinel_pull.sock',
        type=str, help='set the socket path'
    )

    parser.add_argument(
        "-T", "--topic", dest='topic', default='sentinel/collect/fwlogs',
        type=str, help='topic'
    )

    parser.add_argument(
        "-l", "--log-file", dest='syslog_file', default='/var/log/iptables', type=str,
        help='specify the syslog file to be parsed'
    )

    parser.add_argument(
        "-f", "--date-format", dest='date_format', default='%Y-%m-%dT%H:%M:%S', type=str,
        help='specify the syslog date format'
    )

    parser.add_argument(
        "-r", "--log-rotate-conf", dest='logrotate_conf', default='/etc/logrotate.d/iptables',
        type=str, help='specify the log rotate config to be triggered'
    )

    parser.add_argument(
        "-d", "--debug", dest='debug', action='store_true', default=False,
        help='use debug output'
    )

    parser.add_argument(
        "-w", "--wan-interfaces", dest='wans', default=None, type=str,
        help='comma separated list of wan interfaces'
    )

    parser.add_argument(
        "-n", "--now", dest='now', action='store_true', default=True,
        help='don\'t use random sleep interval (this is default behavior)'
    )

    parser.add_argument(
        "--random-sleep", dest='now', action='store_false', default=True,
        help='Use random sleep interval'
    )

    return parser
