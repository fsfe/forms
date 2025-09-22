# =============================================================================
# Build instructions for the Docker container
# =============================================================================
# This file is part of the FSFE Form Server.
#
# SPDX-FileCopyrightText: 2020 FSFE e.V. <contact@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# =============================================================================
# Create requirements.txt file
# =============================================================================
FROM python:3.10-alpine as requirements-builder
WORKDIR /root
ENV PATH="$PATH:/root/.local/bin"

# Upgrade / install pipx
RUN python3 -m pip install --user pipx
RUN python3 -m pipx ensurepath

# Install pipenv with pipx
RUN python3 -m pipx install pipenv

# Import Python packages
COPY Pipfile Pipfile.lock ./

# Create requirements.txt for the next step
RUN pipenv requirements > requirements.txt

# =============================================================================
# Install dependencies
# =============================================================================
FROM python:3.10-alpine as dependencies

EXPOSE 8080

WORKDIR /root
RUN apk add --no-cache git
# FIXME: should not be nescessary
RUN pip install more-itertools

COPY --from=requirements-builder /root/requirements.txt ./
RUN pip install --ignore-installed setuptools pip
RUN pip install wheel
RUN pip install --no-cache-dir -r requirements.txt
# Install the actual application
COPY . .
RUN ./setup.py install

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

FROM development as production

# Run the WSGI server
CMD gunicorn --bind 0.0.0.0:8080 "fsfe_forms:create_app()"
