# =============================================================================
# Build instructions for the Docker container
# =============================================================================
# This file is part of the FSFE Form Server.
#
# SPDX-FileCopyrightText: 2020 FSFE e.V. <contact@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# =============================================================================
# Install dependencies
# =============================================================================
FROM bitnami/python:3.9 as dependencies

EXPOSE 8080

WORKDIR /root

COPY requirements.txt ./
RUN pip install --ignore-installed setuptools pip
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Development installation
# =============================================================================

FROM dependencies AS development

# Switch to non-root user
RUN adduser --uid 1000 --gecos "FSFE" --shell "/sbin/nologin" --disabled-password fsfe
USER fsfe
WORKDIR /home/fsfe

# =============================================================================
# Production installation
# =============================================================================

FROM staging as production

# Install the actual application
COPY . .
RUN ./setup.py install

# Run the WSGI server
CMD gunicorn --bind 0.0.0.0:8080 "fsfe_forms:create_app()"
