#!/usr/bin/env python3
# =============================================================================
# Install the FSFE Form Server locally
# =============================================================================
# This file is part of the FSFE Form Server.
#
# Copyright © 2017-2019 Free Software Foundation Europe <contact@fsfe.org>
#
# The FSFE Form Server is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# The FSFE Form Server is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details <http://www.gnu.org/licenses/>.
# =============================================================================

from setuptools import setup


setup(
    name="fsfe-forms",
    description="FSFE Form Server",
    url="https://git.fsfe.org/fsfe-system-hackers/forms",
    author="Free Software Foundation Europe",
    author_email="contact@fsfe.org",
    license="GPL",
    packages="fsfe_forms",
    include_package_data=True,
    zip_safe=False
)
