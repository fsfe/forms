<!--
SPDX-FileCopyrightText: 2020 Free Software Foundation Europe <contact@fsfe.org>

SPDX-License-Identifier: CC-BY-SA-4.0
-->

# How to install fsfe-forms

## Requirements

The file [`Pipfile`] lists all Python dependencies of fsfe-forms, and
[`Pipfile.lock`] contains information about the actual versions of these
dependencies recommended for use. You can use `pipenv install --system` to
download and install all these dependencies on your computer.

Please note that fsfe-forms requires access to a number of external systems
to run properly, most notably a mail server, a redis server, and for some
functions the FSFE Community Database Frontend.


## Local install

Run `./setup.py install` in the git checkout directory to install fsfe-forms
on the local machine. There are a number of options to select the installation
target, for example installing with a specific prefix, or installing in a home
directory to be able to install without root permissions. Run `./setup.py
install --help` for more information. Run `./setup.py --help-commands` for a
list of other tasks you can do with `setup.py`.

[`setup.py`] installs all Python files and uses [`MANIFEST.in`] to determine
which additional files to install.


## Docker image build

The [`Dockerfile`] contains build instructions for a Docker container in which
fsfe-forms can run. After installing the requirements, it installs fsfe-forms
using `setup.py install`, all as described in the previous sections.

Within the Docker container, fsfe-forms runs as non-privilleged user “fsfe” for
security reasons.


## Automatic deployment

fsfe-forms uses [drone](https://drone.fsfe.org) to automatically deploy updates
to the production server.

Upon each push to the master branch of the git repository, drone creates a
temporary clone of the repository and then sequentially executes the following
steps defined in [`.drone.yml`]:

1. *build-quality*: use [`docker-compose`] with [`docker-compose-quality.yml`]
   as a wrapper around [`Dockerfile-quality`] to create a docker image for
   automatic quality checks.

2. *quality*: in a container with the previously created image, run a number of
   quality checks to ensure no obviously broken code is deployed to the
   production server.

3. *deploy*: again, use [`docker-compose`], this time to create the actual
   docker image and start the corresponding container. The file
   [`docker-compose.yml`] defines the parameters for this step, referring to
   the [`Dockerfile`] described in the previous section.


### Secrets

The following secrets are [managed in drone](http://docs.drone.io/manage-secrets/):

<table>
  <tr>
    <th>Name</th>
    <th>Description</th>
    <th>Requirement</th>
  </tr>
  <tr>
    <th>fsfe_cd_passphrase</th>
    <td>
      Passphrase to verify URL-based commands to the FSFE Community Database
    </td>
    <td>Must match the “cmd_passphrase” secret of fsfe-cd-back.</td>
  </tr>
</table>


[`Pipfile`]: ../Pipfile
[`Pipfile.lock`]: ../Pipfile.lock
[`setup.py`]: ../setup.py
[`MANIFEST.in`]: ../MANIFEST.in
[`Dockerfile`]: ../Dockerfile
[`Dockerfile-quality`]: ../Dockerfile-quality
[`docker-compose`]: https://docs.docker.com/compose/
[`docker-compose.yml`]: ../docker-compose.yml
[`docker-compose-quality.yml`]: ../docker-compose-quality.yml
[`.drone.yml`]: ../.drone.yml
