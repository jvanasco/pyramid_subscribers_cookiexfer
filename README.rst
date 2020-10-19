pyramid_subscribers_cookiexfer
==============================

Build Status: ![Python package](https://github.com/jvanasco/pyramid_subscribers_cookiexfer/workflows/Python%20package/badge.svg)


This package is likely no longer necessary and likely to be EOL.

`pyramid_subscribers_cookiexfer` allows you to transfer cookies from the request
to the response on an http exception, and persist set-cookie data through
serverside sessions.

Originally, this package designed to deal with two scenarios:

1. The Safari browser did not respect Set-Cookie headers on 302 an 303 redirects.
   This was changed around 2012, and there are very few "wrong" browsers in the wild.
   To get around this situation, this library stashed the SetCookie data into a
   server-side session, and then re-integrated it on the next view.

2. Much earlier versions of Pyramid had drastically different behaviors between

.. code-block:: python

	return HTTPFound("/path/to")    

and

.. code-block:: python

	raise HTTPFound("/path/to")    

   This is no longer the case, for as many as 10 years.

If we went back in time...

You may need this if your application code rewrites a response, as cookies are
often set with `add_response_callback` and not `add_finished_callback`.

You may also need this to support some browsers which ignore cookies on certain
status codes.

If you only persist data through a serversside Pyramid session, this pacakge
is not needed. The Pyramid session cookie is often set before authentication,
so data persists through the redirect.

Overview
--------

This package may be useful if you are setting ancillary information through
browser cookies, such as caching user data on the client.

A typical user flow might be this:

* user submits form to /account/login
* backend authenticates, sets various cookies
* backend redirects to /account/home

Almost every browser respects a `SetCookie` header on a redirect -- however
Safari is known to ignore this.

Many developers have stored cookies in session data to show on future visits,
this package automates that.

Two methods are available to persist information

* `add_headers` Transfers cookie headers from the request to the response
* `session_save` Saves the cookies you'd want to set into the session, migrates
  them into the response on the next pageview

This package also offers the ability to uniquely manage the cookies to avoid
duplicates.  right now this behavior is recommended.

The package is configured through a few variables set in your `.ini` files , then
enabled with an import and call to `initialize` in your `.ini`

The internal mechanics are pretty simple:

.. code-block:: python

    config.add_subscriber(new_request, 'pyramid.events.NewRequest')
    config.add_subscriber(new_response, 'pyramid.events.NewResponse')

In order to aid in debugging and cut down on processing:

* `initialize_subscribers()` will only install a `NewResponse` listener if
  sessioning will be used
* A configurable regex is used to eliminate paths from the
  module (including debug statements)

Important Notes:

* This package will respect headers that are raised with the httpexception
* Because of how pyramid's internals work, you must `return` the redirect
  -- not `raise` it -- if you want cookies transferred from the `request.response`.
  If you "raise" a redirect, only the headers used to initialize the redirect
  can be stored in the session (they exist in the new response object and do not
  need to be transferred)

These situations will work:

A few case examples

.. code-block:: python

	`return HTTPFound(location='/new/location')`

* Any cookies set by `request.response.set_cookie` will be transferred

.. code-block:: python

	`return HTTPFound(location='/new/location', headers=dict_of_headers)`

* the headers in `dict_of_headers` are already in the new `response`, and can persist to the `session`
* any cookies set by `request.response.set_cookie` will be transferred

.. code-block:: python

	`raise HTTPFound(location='/new/location')`

* NO cookies set by `request.response.set_cookie` will be transferred

.. code-block:: python

	`raise HTTPFound(location='/new/location', headers=dict_of_headers )`

* the headers in `dict_of_headers` are already in the new `response`, and can persist to the `session`
* NO cookies set by `request.response.set_cookie` will be transferred


configuration options
---------------------

.. code-block:: python

	`cookie_xfer.re_excludes`

If set, this will be compiled into a regex. routes matching this regex will be ignored.

.. code-block:: python

	`cookie_xfer.redirect_add_headers`

If "true", 



setup
-----

environment.ini

.. code-block:: python

    cookie_xfer.redirect_add_headers = True
    cookie_xfer.redirect_session_save = False
    cookie_xfer.apply_unique = False
    cookie_xfer.re_excludes = "^/(css|img|js|deform|_debug_toolbar)"


app/__init__.py

.. code-block:: python

    import pyramid_subscribers_cookiexfer

    def main(global_config, **settings):
        ...
        config.include("pyramid_subscribers_cookiexfer")
        ...

