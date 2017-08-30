# forms API

The forms API, available under <https://forms.fsfe.org> can be used to send
form data from a web page submission, via email, to somewhere else. The API
is highly configurable and can be adapted for a wide variety of situations
in which you need to send emails form a web page, either with or without
double opt-in.

Each application which intends to use this service must be registered in
the API configuration, which is available in `src/configuration/applications.json`.

## Supported parameters for each registered application user

Most of the parameters which are available for an application can be set
*either* in the API configuration, or in the GET request when calling the
API. If a parameter is specified in the API configuration, this takes
precendence. So for instance, if the API configuration sets the To
address as `nobody@example.com`, then even if the request includes
`to=foo@example.com`, this will be ignored, and the To address set
according to the API configuration.

These are the available parameters for configuration or request:

 * **from**: sets an explicit From address on emails sent
 * **to**: one or more recipients, explicit To address
 * **replyto**: sets an explicit Reply-To header on emails sent
 * **subject**: sets the Subject of an email
 * **content**: sets the content (plain text) of an email
 * **template**: defines which template file to use as content

If both **content** and **template** is set, then **template** will be used
instead.

The following parameters are available only in the API configuration file:

 * **ratelimit**: controls the number of emails allowed to be sent per hour
 * **include_vars**: if set to true, then any extra variables provided in a GET request will be made available to the template when rendering an email
 * **store**: if set to a filename, then information about emails sent will be stored in this file. This will not inclue emails which have not been confirmed (if double opt-in is in use).
 * **confirm**: if set to true, then no email is sent without an explicit confirmation of a suitable e-mail address. The email to confirm should be passed in the **confirm** parameter of the GET request (see later)
 * **redirect**: address to redirect the user to after having accepted and processed a request


## Typical uses

### Sending a ticket to our ticket system

You're writing a page in which you would like to create a form where
submission of that form creates a ticket in our ticket system. There's
no need for an opt-in for this, and we don't want to store information
outside of the ticket system.

The configuration could look like this:

```json
  "totick2": {
    "ratelimit": 500,
    "to": [ "contact@fsfe.org" ],
    "subject": "Registration of event",
    "include_vars": true,
    "redirect": "http://fsfe.org",
    "template": "totick2-template"
  },
```

The HTML form could look like this:

```html
<form method="POST" action="https://forms.fsfe.org/email">
  Your e-mail: <input type="email" name="from" />
  Your country: <input type="text" name="country" />
  Your message: <input type="text" name="message" />
</form>
```

And finally, the template:

```
Hi!

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
    "to": [ "campaignowner@fsfe.org" ],
    "subject": "New signatory to open letter",
    "include_vars": true,
    "redirect": "http://fsfe.org",
    "template": "tosign-template",
    "store": "/store/campaign2.json",
    "confirm": true,
  },
```

The HTML form could look like this:

```html
<form method="POST" action="https://forms.fsfe.org/email">
  Please sign our open letter here!

  Your name: <input type="text" name="name" />
  Your e-mail: <input type="email" name="confirm" />
  Your country: <input type="text" name="country" />
</form>
```

And finally, the template:

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
"reply-to": null}
```

In the future we hope this json data will also contain the included variables
to make them easier to parse.




## Supported API calls

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

