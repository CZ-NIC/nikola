#
# Nikola - firewall log sender (a part of www.turris.cz project)
# Copyright (C) 2013 CZ.NIC
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

import logging
import logging.handlers


def get_logger(debug=False):

    # get logger name
    logger = logging.getLogger("nikola")

    # add syslog handler
    sys_handler = logging.handlers.SysLogHandler(address="/dev/log")

    # set logging format
    sys_handler.setFormatter(logging.Formatter('%(name)s: %(levelname)s %(msg)s'))
    logger.addHandler(sys_handler)

    # add console handler
    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)

    # set debug
    if debug:
        logger.setLevel(logging.DEBUG)

    return logger
