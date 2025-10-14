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
FROM python:3.14-alpine AS requirements-builder
WORKDIR /root

COPY Pipfile Pipfile.lock ./

# Install pipenv via pipx
RUN apk add --no-cache pipx
ENV PATH="$PATH:/root/.local/bin"
RUN pipx install pipenv

RUN pipenv requirements > requirements.txt

# =============================================================================
# Install dependencies
# =============================================================================
FROM python:3.14-alpine AS dependencies

EXPOSE 8080

WORKDIR /root
RUN apk add --no-cache git

COPY --from=requirements-builder /root/requirements.txt ./
RUN pip install --ignore-installed setuptools
RUN pip install wheel
RUN pip install --no-cache-dir -r requirements.txt
# Install the actual application
COPY . .
RUN pip install .

# =============================================================================
# Development installation
# =============================================================================

FROM dependencies AS development

# Switch to non-root user
RUN adduser --system forms --uid 1000
WORKDIR /tmp
USER forms

# =============================================================================
# Production installation
# =============================================================================

FROM development AS production

# Run the WSGI server
CMD gunicorn --bind 0.0.0.0:8080 "fsfe_forms:create_app()"
