#!/usr/bin/env python3
# =============================================================================
# Install the FSFE Form Server locally
# =============================================================================
# This file is part of the FSFE Form Server.
#
# SPDX-FileCopyrightText: 2020 FSFE e.V. <contact@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup


setup(
    name="fsfe-forms",
    description="FSFE Form Server",
    url="https://git.fsfe.org/fsfe-system-hackers/forms",
    author="Free Software Foundation Europe",
    author_email="contact@fsfe.org",
    license="GPL",
    packages=["fsfe_forms",
                "fsfe_forms.static.css",
                "fsfe_forms.static.img",
                "fsfe_forms.templates",
                "fsfe_forms.templates.pages"],
    include_package_data=True,
    zip_safe=False
)
