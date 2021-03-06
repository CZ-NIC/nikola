#!/usr/bin/env python
#
# nikola - firewall log sender (a part of www.turris.cz project)
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

from setuptools import setup

from sentinel_nikola import __version__


setup(
    name='sentinel-nikola',
    version=__version__,
    author='CZ.NIC, z.s.p.o. (http://www.nic.cz/)',
    author_email='packaging@turris.cz',
    packages=['sentinel_nikola', ],
    url='https://gitlab.labs.nic.cz/turris/nikola',
    license='GPLv3+',
    description='Sentinel Nikola package for TurrisOS',
    long_description=open('README.txt').read(),
    entry_points={
        "console_scripts": [
            "sentinel-nikola = sentinel_nikola.__main__:main",
        ]
    },
    zip_safe=False,
)
