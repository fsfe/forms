<!--
SPDX-FileCopyrightText: 2020 Free Software Foundation Europe <contact@fsfe.org>

SPDX-License-Identifier: CC-BY-SA-4.0
-->

# How to hack on fsfe-forms

## Development environment setup

The (strongly) recommended way of developing, testing and debugging fsfe-forms
is to set up an isolated Python environment using docker containers.
This will make development independent from the operating system provided
version of the required Python libraries.

After cloning the git repository, just run `make dev` in the git checkout
directory and the container environment will be completely set up.

## Coding style

fsfe-forms follows [PEP 8](https://pep8.org/). Additionally, imports are sorted
alphabetically; you can run `make isort.all` to let
[isort](https://pypi.org/project/isort/) check if your imports are sorted corectly.

## Testing and debugging environment

fsfe-forms can be run from the git checkout directory for testing and
debugging.

Please note that fsfe-forms requires access to a number of external systems
to run properly, most notably a mail server, a redis server, and for some
functions the FSFE Community Database Frontend.

These are set up for you in separate containers.

## Automatic quality checks

The following commands are available for automatic quality checks:

* `make isort.all` to verify the correct sorting of imports.
* `make lint.all` to verify the compliance with coding standards.
* `make pytest.all` to run the functional tests defined in the [tests](../tests)
  directory.
* `make qc.all` to run all of the above tests.

All these tests are also run during the deployment process, and updating the
code on the production server is refused if any of the tests fails, so it is
strongly recommended that you run `make qc.all` before committing any change.
