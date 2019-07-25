# How to configure fsfe-forms

Configuration parameters for fsfe-forms must be set through environment
variables.

The configuration for the production instance of fsfe-forms is set in
[`docker-compose.yml`]. On the other hand, the file [`.env`], which is read
automatically when entering the “pipenv” virtual environment, contains settings
suitable for testing and debugging.


## Flask server settings

These settings are only relevant for the Flask builtin web server, which is
very nice for testing and debugging, but not recommended for production.


### `FLASK_SKIP_DOTENV`

In the virtual environment setup used for the development of fsfe-forms, the
.env file is parsed by `pipenv`, so we always set this to `1`.


### `FLASK_APP`

This tells the Flask server where to find the application object. Always set to
`fsfe_cd_front`.


### `FLASK_ENV`

Since we don't use the Flask server for production, this is always set to
`development`.


### `FLASK_RUN_HOST`

The hostname to listen on.


### `FLASK_RUN_PORT`

The TCP port to listen on.


## Email settings

### `MAIL_SERVER` and `MAIL_PORT`

The SMTP server and port to use for sending out all kinds of emails. Defaults
to `localhost` and `25`.


### `MAIL_USERNAME` and `MAIL_PASSWORD`

The credentials for the SMTP server. Only needed if the SMTP server requires
authentication.


### `LOG_EMAIL_FROM` and `LOG_EMAIL_TO`

In a production environment, fsfe-forms sends log messages of severity
“ERROR” or worse by email. These are the “From” and “To“ address for these
emails.


## Parameters for the connection to the Redis server

### `REDIS_HOST` and `REDIS_PORT`

Hostname and TCP port of the Redis server.


[`docker-compose.yml`]: ../docker-compose.yml
[`.env`]: ../.env
