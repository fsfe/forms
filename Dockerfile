# SPDX-FileCopyrightText: 2020 FSFE e.V. <contact@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Create requirements.txt file
FROM python:3.14-alpine AS requirements-builder
WORKDIR /root

COPY Pipfile Pipfile.lock ./

# Install pipenv via pipx
RUN apk add --no-cache pipx
ENV PATH="$PATH:/root/.local/bin"
RUN pipx install pipenv

RUN pipenv requirements > requirements.txt

# Install dependencies using requirements.txt
FROM python:3.14-alpine AS dependencies
WORKDIR /root

RUN apk add --no-cache git py3-setuptools py3-wheel

COPY --from=requirements-builder /root/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# Install the actual application
COPY . .
RUN pip install .


FROM dependencies AS development

# Switch to non-root user
RUN adduser --system forms --uid 1000
WORKDIR /tmp
USER forms


FROM development AS production
EXPOSE 8080

# Run the WSGI server
CMD gunicorn --bind 0.0.0.0:8080 "fsfe_forms:create_app()"
