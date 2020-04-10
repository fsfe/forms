<!--
SPDX-FileCopyrightText: 2020 Free Software Foundation Europe <contact@fsfe.org>

SPDX-License-Identifier: CC-BY-SA-4.0
-->

# How to configure fsfe-forms

Configuration parameters for fsfe-forms can be set through environment
variables.

For testing and debugging, the default configuration should be suitable for
many use cases. If you need to explicity set any of the parameters, you can
create a `.env` file in the project root directory, which will automatically be
read whenever the "pipenv" virtual environment is entered.

The configuration for the production instance of fsfe-forms is set in
[`docker-compose.yml`].


## Ratelimit settings

### `RATELIMIT_DEFAULT`

The default rate limit in the format described
[here](https://flask-limiter.readthedocs.io/en/stable/#ratelimit-string).
Defaults to no rate limit.


## Email settings

### `MAIL_SERVER` and `MAIL_PORT`

The SMTP server and port to use for sending out all kinds of emails. Defaults
to `localhost` and `25`.


### `MAIL_USERNAME` and `MAIL_PASSWORD`

The credentials for the SMTP server. Only needed if the SMTP server requires
authentication. Defaults to no authentication.


### `LOG_EMAIL_FROM` and `LOG_EMAIL_TO`

In a production environment, fsfe-forms sends log messages of severity
“ERROR” or worse by email. These are the “From” and “To“ address for these
emails. No default.


## Parameters for the connection to the Redis server

### `REDIS_HOST` and `REDIS_PORT`

Hostname and TCP port of the Redis server. Defaults to `localhost` and `6379`.

### `REDIS_PASSWORD`

Optional password for the Redis connection. Defaults to no password.

### `REDIS_QUEUE_DB`

Redis database number for the double opt-in queue. Defaults to `0`.


## Parameters for the connection to the FSFE Community Database

### `FSFE_CD_URL`

URL of the FSFE Community Database Frontend. Defaults to
`http://localhost:8089`, which is where a locally running test instance of
fsfe-cd-back can be found.

### `FSFE_CD_TIMEOUT`

Timeout, in seconds, for connecting to the FSFE Community Database Frontend.
Defaults to 3.

### `FSFE_CD_PASSPHRASE`

Passphrase for sending commands to the FSFE Community Database Frontend.


[`docker-compose.yml`]: ../docker-compose.yml
