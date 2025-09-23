# SPDX-FileCopyrightText: 2025 Filip Kobierski <fkobi@fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

FROM python:alpine

COPY ./config /config
EXPOSE 8888

# required for mock-server
RUN apk add --no-cache build-base

RUN pip install mock-server
CMD mock-server --dir=/config -address=0.0.0.0
