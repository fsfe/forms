# forms API

[![Build Status](https://drone.fsfe.org/api/badges/fsfe-system-hackers/forms/status.svg)](https://drone.fsfe.org/fsfe-system-hackers/forms)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

The forms API, available under <https://forms.fsfe.org> can be used to send
form data from a web page submission, via email, to somewhere else. The API
is highly configurable and can be adapted for a wide variety of situations
in which you need to send emails from a web page, either with or without
double opt-in.

Each application which intends to use this service must be registered in
the API configuration, which is available in `src/configuration/applications.json`.

## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [API](#api)
- [Contribute](#contribute)
- [License](#license)

## Install

It is not expected that you install the forms API code yourself, but if you
choose to do so, you will be expected to install and run both the worker and
web app. Both need access to a Redis. The web app takes care of the frontend
API, whereas the worker is responsible for actually sending out emails.

To setup the environment:

```
$ export REDIS_HOST=redishostname
$ export REDIS_PORT=redispost
$ export REDIS_PASSWORD=redispassword  # if required
$ pip install -r requirements.txt
```

You can then run the web app with:

```
src/$ gunicorn -b 0.0.0.0:8080 wsgi:application
```

This will run the web application on port 8080 on the default network
interface. Starting the background worker is done with:

```
src/$ python worker.py worker -l info
```

## Usage

### Sending a ticket to our ticket system

You're writing a page in which you would like to create a form where
submission of that form creates a ticket in our ticket system. There's
no need for an opt-in for this, and we don't want to store information
outside of the ticket system.

The application configuration could look like this:

```json
  "totick2": {
    "ratelimit": 500,
    "to": [ "contact@fsfe.org" ],
    "subject": "Registration of event from {{ participant_name }}",
    "include_vars": true,
    "redirect": "http://fsfe.org",
    "template": "totick2-template",
    "required_vars": ["participant_name"],
    "headers": {
      "X-OTRS-Queue": "Promo"
    }
  },
```

The template configuration could look like this:

```json
  "totick2-template": {
    "plain": {
      "filename": "totick2-template.txt"
    },
    "required_vars": ["country", "message", "participant_name"],
    "headers": {
      "X-PARTICIPANT-NAME": "{{ participant_name }}"
    }
  }
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

And finally, the template (totick2-template.txt):

```
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
    "ratelimit": 500,
    "from": "admin@fsfe.org",
    "confirmation-from": "admin@fsfe.org",
    "to": [ "campaignowner@fsfe.org" ],
    "subject": "New signatory to open letter",
    "include_vars": true,
    "redirect": "http://fsfe.org",
    "template": "tosign-template",
    "store": "/store/campaign2.json",
    "confirm": true,
  },
```

The template configuration could look like this:

```json
  "tosign-template": {
    "plain": {
      "filename": "tosign-template.txt",
    },
    "required_vars": ["name", "confirm", "country"]
  }
```

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

And finally, the template (tosign-template.txt):

```
Hi!

I support your work and sign your open letter about X!

  {{ name }} <{{ confirm }}> from {{ country }}.
```

When someone submits the form, a mail will first be sent to the address
given. The e-mail will have the following form:

```
You've requested the following e-mail to be sent on your behalf.

"Hi!

I support your work and sign your open letter about X!

  John Doe <john@example.com> from Switzerland.
"

To confirm, please click the following link. If you do not click
this link to confirm, your mail will not be sent.

https://forms.fsfe.org/confirm?id=randomnumber
```

No information will be stored, and no email sent to the To address before
the user clicks that URL. When the URL is clicked, the email will be sent
to <campaignowner@fsfe.org> as given in the configuration, and a JSON
file `/store/campaign2.json` will be created with the following content:

```json
{"from": "admin@fsfe.org", "to": ["campaignowner@fsfe.org"], "subject": "New signatory to open letter",
"content": "Hi!\n\nI support your work and sign your open letter about X!\n\n  John Doe <john@example.com> from Switzerland.\n",
"reply-to": null,
"include_vars": {"name": "John Doe", "confirm": "john@example.com", "country": "Switzerland"}}
```

### Multi lang (optional)

If you want to send an email in a specific language you have to add an hidden field in your form:
`<input type="hidden" name="lang" value="it">`

Moreover you have to update the configuration fields:
- `subject` and `confirmation-subject`: in a dict `
  {"de": "....", "fr": "...", "en": "..."}
`
- `filename`: with the template `filename.{lang}.txt` (ex: `totick2-template.{lang}.txt`)

Rules:
- If a request provides the `lang` argument:
  - The API searches the `subject` and `confirmation-subject` in the hash provided in the configuration file and returns it
  - The API replaces the `{lang}` (in `filename.{lang}.txt`) with the language provided in the request
- If no argument `lang` is received (or is not provide in conf):
  The API returns missing elements (subject, confirmation-subject, file) in English (replace `{lang}` by 'en').

## API

### POST/GET https://forms.fsfe.org/email

This will trigger the sending of an email, potentially with a double opt-in
according to the configuration. The following parameters are supported:

 * appid (required)
 * from
 * to
 * replyto
 * subject
 * content
 * template
 * confirm (required for some appid)

### GET https://forms.fsfe.org/confirm

This will confirm an e-mail address if using double opt-in. The following
parameters are supported:

 * confirm (required)

The value for confirm is generated automatically by the forms system. You
should never need to generate this URL yourself.

### Supported parameters for each registered application user

Most of the parameters which are available for an application can be set
*either* in the API configuration, or in the GET request when calling the
API. If a parameter is specified in the API configuration, this takes
precendence. So for instance, if the API configuration sets the To
address as `nobody@example.com`, then even if the request includes
`to=foo@example.com`, this will be ignored, and the To address set
according to the API configuration.

These are the available parameters for configuration or request:

 * **from**: sets an explicit From address on emails sent. Could contain variables
 * **to**: one or more recipients, explicit To address. Could contain variables
 * **replyto**: sets an explicit Reply-To header on emails sent
 * **subject**: sets the Subject of an email. Could contain variables
 * **content**: sets the content (plain text) of an email. Could contain variables
 * **template**: defines which template configuration will be used to provide content. Could contain variables

If both **content** and **template** is set, then **template** will be used
instead.

The following parameters are available only in the API configuration file:

 * **ratelimit**: controls the number of emails allowed to be sent per hour
 * **include_vars**: if set to true, then any extra variables provided in a GET request will be made available to the template when rendering an email
 * **store**: if set to a filename, then information about emails sent will be stored in this file. This will not inclue emails which have not been confirmed (if double opt-in is in use).
 * **confirm**: if set to true, then no email is sent without an explicit confirmation of a suitable e-mail address. The email to confirm should be passed in the **confirm** parameter of the GET request (see later)
 * **redirect**: address to redirect the user to after having accepted and processed a request
 * **redirect-confirmed**: address to redirect the user to after the user has confirmed their email (if using confirm==true)
 * **required_vars**: an array with parameter names that has to be presented in request parameters
 * **headers**: a key-value dictionary that should be included to email as headers. Values could contain variables
 * **confirmation-template**: name of a template defined in templates config that will be used as confirmation email. For confirmation emails already provided 2 variables: "confirmation_url" and "content". Content is the rendered email that will be sent after confirmation
 * **confirmation-duplicate-template**: name of a template defined in templates config that will be used for user that want make multiples signatures
 * **confirmation-subject**: custom subject for confirmation email. Could contain variables
 * **confirmation-duplicate-subject**: custom subject for duplicate confirmation email. Could contain variables
 * **confirmation-check-duplicates**: set to `true` to the check whether the email already confirmed (duplicated). Disabled by default

## Contribute

In order to contribute, a local testing setup is very useful. All you need is Docker and docker-compose. In the repository, just run `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build` to spin up the three default containers this application includes and an extra "fake SMTP" for local testing.

### Fake SMTP server

To test emails, you are recommended to use `fake-smtp-server` linked as submodule in this repository. It allows you to use a local SMTP server which does not send the emails but lists them in your browser. Doing this, you can view and debug sent emails without having to set up this service.

The above command using the extra file `docker-compose.dev.yml` sets this up automatically.

More info on the fake smtp server on [its official website](https://www.npmjs.com/package/fake-smtp-server).

### Use the service locally

After running docker-compose, you can access all services locally:

* forms-web: http://localhost:8080
* forms-fakesmtp: http://localhost:1080

Now you either replace the URLs of a form with `http://localhost:8080/email` (for example in your browser with developer tools), or send POST requests via curl like: `curl -X POST "http://localhost:8080/email" -d "appid=pmpc-sign&name=tester1&confirm=mail@example.com&permissionPriv=yes"`.

On `http://localhost:1080` you can then see the sent emails.

## License

This software is copyright 2019 by the Free Software Foundation Europe e.V.
and licensed under the GPLv3 license. For details see the "LICENSE" file in
the top level directory of https://git.fsfe.org/fsfe-system-hackers/forms/

