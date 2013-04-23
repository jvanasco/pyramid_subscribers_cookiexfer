pyramid_subscribers_cookiexfer allows you to transfer cookies from the request to the response on an http exception.  you might need this as redirects are subclasses of httpexceptions.

overview
--------

a typical user flow might be this:

* user submits form to /account/login 
* backend authenticates, sets various cookies
* backend redirects to /account/home

if you only persist data through pyramid sessions this is not needed -- the pyramid session cookie is set before authentication, so data persists through the redirect.

this is useful if you're setting ancillary information through browser cookies , such as caching user data on the client.

Almost every browser respects a SetCookie header on a redirect -- only Safari is known to ignore this.  Many developers have stored cookies in session data to show on future visits, this package automates that.

two methods are available to persist information

- add_headers -- transfers cookie headers from the request to the response
- session_save -- saves the cookies you'd want to set into the session, migrates them into the response on the next pageview

additionally the package offers the ability to 'uniquely' manage the cookies to avoid duplicates.  right now this behavior is recommended.

the package is configured through a few variables set in your .ini files , then enabled with an import and call to 'initialize' in your .ini

the internal mechanics are pretty simple:

    config.add_subscriber(\
        new_request, 
        'pyramid.events.NewRequest')
    config.add_subscriber(\
        new_response, 
        'pyramid.events.NewResponse')
    
in order to aid in debugging and cut down on processing:

- initialize_subscribers() will only install a NewResponse listener if sessioning will be used
- a configurable regex is used to eliminate paths from the module ( including debug statements )

Important Notes:

- This package will respect headers that are raised with the httpexception
- Because of how pyramid's internals work, you must 'return' the redirect -- not 'raise' it -- if you want cookies transferred from the request.response.  If you 'raise' a redirect, only the headers used to initialize the redirect can be stored in the session ( they exist in the new response object and do not need to be transferred )

These situations will work: 

A few case examples

    return HTTPFound(location='/new/location') 
    - any cookies set by request.response.set_cookie will be transferred
    
    return HTTPFound(location='/new/location', headers=dict_of_headers ) 
    - the headers in dict_of_headers are already in the new response , and can persist to the session
    - any cookies set by request.response.set_cookie will be transferred
    
    raise HTTPFound(location='/new/location') 
    - NO cookies set by request.response.set_cookie will be transferred

    raise HTTPFound(location='/new/location', headers=dict_of_headers ) 
    - the headers in dict_of_headers are already in the new response , and can persist to the session
    - NO cookies set by request.response.set_cookie will be transferred




setup
-----


environment.ini
    cookie_xfer.redirect_add_headers = True
    cookie_xfer.redirect_add_headers__unique = True
    cookie_xfer.redirect_session_save = False
    cookie_xfer.redirect_session_save__unique = False
    cookie_xfer.re_excludes = "^/(css|img|js|deform|_debug_toolbar)"
    

app/__init__.py

    import pyramid_subscribers_cookiexfer
    
    def main(global_config, **settings):
        ...
        pyramid_subscribers_cookiexfer.initialize( config , settings )
        ...