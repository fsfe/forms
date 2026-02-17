<!--
SPDX-FileCopyrightText: 2020 Free Software Foundation Europe <contact@fsfe.org>
SPDX-FileCopyrightText: 2019 Florian Vuillemot <florian.vuillemot@fsfe.org>

SPDX-License-Identifier: CC-BY-SA-4.0
-->

# forms API

[![in docs.fsfe.org](https://img.shields.io/badge/in%20docs.fsfe.org-OK-green)](https://docs.fsfe.org/repodocs/forms/00_README)
[![Build Status](https://drone.fsfe.org/api/badges/fsfe-system-hackers/forms/status.svg)](https://drone.fsfe.org/fsfe-system-hackers/forms)
[![REUSE status](https://api.reuse.software/badge/git.fsfe.org/fsfe-system-hackers/forms)](https://api.reuse.software/info/git.fsfe.org/fsfe-system-hackers/forms)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

The forms API, available under <https://forms.fsfe.org> can be used to send
form data from a web page submission, via email, to somewhere else. The API
is highly configurable and can be adapted for a wide variety of situations
in which you need to send emails from a web page, either with or without
double opt-in.

Each application which intends to use this service must be registered in
the API configuration, which is available in `fsfe_forms/applications.json`.

## Table of Contents

- [Usage](#usage)
- [API](#api)
- [Contribute](#contribute)

## Usage

### Sending a ticket to our ticket system

You're writing a page in which you would like to create a form where
submission of that form creates a ticket in our ticket system. There's
no need for an opt-in for this, and we don't want to store information
outside of the ticket system.

The application configuration could look like this:

```json
  "totick2": {
    "parameters": {
      "participant_name": ["required", "single-line"],
      "from": ["email"],
      "country": [],
      "message": ["required"]
    }
    "register": {
      "email": "totick2-template",
      "redirect": "https://fsfe.org"
    }
  },
```

The HTML form could look like this:

```html
<form method="POST" action="https://forms.fsfe.org/email">
  <!-- Parameter "appid" is required to identify what application configuration is used to send email -->
  <input type="hidden" name="appid" value="totick2">
  Your name: <input type="text" name="participant_name">
  Your e-mail: <input type="email" name="from" />
  Your country: <input type="text" name="country" />
  Your message: <input type="text" name="message" />
</form>
```

And finally, the template (`totick2-template.eml`):

```eml
From: {{ format_email(participant_name, from) }}
To: contact@fsfe.org
Subject: Registration of event from {{ participant_name }}
X-OTRS-Queue: "Promo"
X-PARTICIPANT-NAME: {{ participant_name }}

Hi!

My name is {{ participant_name }}.
I'm from {{ country }} and would like you to know:

  {{ message }}
```

### Signing an open letter

In this case, we're publishing an open letter which we invite people to
sign. We want to store information about who has signed the open letter,
and we want a double opt-in of their email address so we know we have
a working e-mail. We don't want to include anyone in the list without them
having confirmed.

The configuration could look like this:

```json
  "tosign": {
    "parameters": {
      "name": ["required", "single-line"],
      "country": []
    }
    "store": "/store/campaign2.json",
    "register": {
      "email": "tosign-register",
      "redirect": "http://fsfe.org"
    }
    "confirm": {
      "email": "tosign-confirm",
      "redirect": "http://fsfe.org"
    }
  },
```

Please note that whenever there's a "confirm" option, a parameter named
"confirm" is implicitly added to the list of parameters.

The HTML form could look like this:

```html
<form method="POST" action="https://forms.fsfe.org/email">
  <!-- Parameter "appid" is required to identify what application configuration is used to send email -->
  <input type="hidden" name="appid" value="tosign">
  Please sign our open letter here!

  Your name: <input type="text" name="name" />
  Your e-mail: <input type="email" name="confirm" />
  Your country: <input type="text" name="country" />
</form>
```

Here, we have two email templates. The first one, `tosign-register.eml`, is used
upon registration of a new sigature:

```eml
From: no-reply@fsfe.org
To: {{ format_email(name, confirm) }}
Subject: Your signature for campaign X

Dear {{ name }},

Than you for supporting your work by signing our open letter about X!
To confirm your signature, please click the following link:

{{ confirmation_url }}

Best regards,
the FSFE
```

The second template, `tosign-confirm.eml`, is then used when the confirmation
link has been clicked:

```
From: admin@fsfe.org
To: campaignowner@fsfe.org
Subject: New signatory to open letter

Hi!

I support your work and sign your open letter about X!

  {{ name }} <{{ confirm }}> from {{ country }}.
```

No information will be stored, and no email sent to the To address before the
user clicks the confirmation URL. When the URL is clicked, the email will be
sent to <campaignowner@fsfe.org> as given in the configuration, and a JSON
file `/store/campaign2.json` will be created with the following content:

```json
[
  {
    "from": "admin@fsfe.org",
    "to": ["campaignowner@fsfe.org"],
    "subject": "New signatory to open letter",
    "content": "Hi!\n\nI support your work and sign your open letter about X!\n\n  John Doe <john@example.com> from Switzerland.\n",
    "reply-to": null,
    "include_vars": {
      "name": "John Doe",
      "confirm": "john@example.com",
      "country": "Switzerland"
    }
  }
]
```

### Multi lang (optional)

If you want to send an email in a specific language you have to add an hidden field in your form:
`<input type="hidden" name="lang" value="it">`

Now, for example when looking for the template "tosign-register", the server
will look for a file named `tosign-register.it.eml`, and if that does not
exist, it will fall back to `tosign-register.eml`.


## API

### POST/GET `/email`

This will trigger the sending of an email, potentially with a double opt-in
according to the configuration.

The parameter "appid" is always required and will select the application from
the configuration file applications.json. All other supported parameters depend
on the selected application.

Please note that for applications requiring double opt-in, the parameter for
the user's email address *must* be called "confirm".


### GET `/confirm`

This will confirm an e-mail address if using double opt-in. The following
parameters are supported:

1. **id** (required) -- generated automatically by the forms system. You
   should never need to generate this URL yourself.


## Application configuration

Configuration of the applications is done in the file `applications.json`. It
contains an object where each key is an application id and the value is the
matching application configuration.

The application configuration is again an object with the following possible
keys:

* **parameters**: An object defining the parameters to be included in a
  request. Required.
* **cd**: An object defining the parameters to be sent to the FSFE Community
  Database, where names are the properties in fsfe-cd and values are the
  matching parameter names in the form. Optional.
* **store**: If set to a filename, then information about emails sent is
  stored in this file. This does not inclue emails which have not been
  confirmed (if double opt-in is in use). Optional.
* **register**: Defines what to do upon registration of a user. Required.
* **confirm**: If present, forces double opt-in, and defines what to do upon
  confirmation of a registration. Optional.
* **duplicate**: If present, forces the check for duplicate registrations, and
  defines what to do when one occurs. Optional.

In the "parameters" object, each key defines a parameter name, where the value
is a list of zero or more validations to apply to this parameter, with the
following being avaliable:

* **required**: must be included and non-empty.
* **single-line**: must not contain line breaks. Use this for all fields that
  are included in email headers to avoid header injection attacks.
* **email**: must look like a valid email address. The actual existence of the
  address is not checked, though.
* **boolean**: must be something that can be understood as a boolean value
  (true/false, t/f, yes/no, y/n, on/off, 1/0).
* **mandatory**: must be a true-ish boolean value. Use this for fields like "I
  agree to the privacy statement".
* **forbidden**: must be empty or not included at all. Use this for honeypot
  entries to catch spam bots.

Each of "register", "confirm", and "duplicate" are again objects with the
following keys:

* **email**: Template for the email to be sent.
* **redirect**: Address to redirect the user's browser to after having
  accepted and processed a request


## Contribute

### Testing in a local docker container

In order to contribute, a local testing setup is very useful. All you
need is Docker and docker-compose. To spin up the three default
containers this application (including and an extra "fake SMTP" for
local testing) run the following command:
```sh
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

#### Fake SMTP server

To test emails, you are recommended to use `fake-smtp-server` linked
as submodule in this repository. It allows you to use a local SMTP
server which does not send the emails but lists them in your
browser. Doing this, you can view and debug sent emails without having
to set up this service.

The above command using the extra file `docker-compose.dev.yml` sets
this up automatically.

More info on the fake smtp server on [its official
website](https://www.npmjs.com/package/fake-smtp-server).

#### Use the service locally

After running docker-compose, you can access all services locally:

* forms-web: http://localhost:8080
* forms-fakesmtp: http://localhost:1080 (see the sent emails here)

Now you either replace the URLs of a form with
`http://localhost:8080/email` (for example in your browser with
developer tools), or send POST requests via curl like:
```sh
curl -X POST \
	"http://localhost:8080/email" \
	-d "appid=pmpc-sign&name=tester1&confirm=mail@example.com&permissionPriv=yes"`
```
