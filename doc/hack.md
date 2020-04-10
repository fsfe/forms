<!--
SPDX-FileCopyrightText: 2020 Free Software Foundation Europe <contact@fsfe.org>

SPDX-License-Identifier: CC-BY-SA-4.0
-->

# How to hack on fsfe-forms

## Development environment setup

The (strongly) recommended way of developing, testing and debugging fsfe-forms
is to set up an isolated Python environment, called a *virtual environment* or
*venv*, to make development independent from the operating system provided
version of the required Python libraries. To make this as easy as possible,
fsfe-forms uses [Pipenv](https://docs.pipenv.org/en/latest/).

After cloning the git repository, just run `make virtualenv` in the git
checkout directory and the virtual environment will be completely set up.


## Coding style

fsfe-forms follows [PEP 8](https://pep8.org/). Additionally, imports are sorted
alphabetically; you can run `make applyisort` to let
[isort](https://pypi.org/project/isort/) do that for you.


## Testing and debugging environment

fsfe-forms can be run from the git checkout directory for testing and
debugging.

Please note that fsfe-forms requires access to a number of external systems
to run properly, most notably a mail server, a redis server, and for some
functions the FSFE Community Database Frontend.

When you have set up all that, you can run `make flask` to run fsfe-forms
with Flask's built-in web server in debug mode. Alternatively, you can run
`make gunicorn` to use the gunicorn web server, which is the variant used in
production.


## Automatic quality checks

The following commands are available for automatic quality checks:

* `make isort` to verify the correct sorting of imports.
* `make lint` to verify the compliance with coding standards.
* `make pytest` to run the functional tests defined in the [tests](../tests)
  directory.
* `make quality` to run all of the above tests.

All these tests are also run during the deployment process, and updating the
code on the production server is refused if any of the tests fails, so it is
strongly recommended that you run `make quality` before committing any change.
