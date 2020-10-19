from __future__ import print_function
from __future__ import unicode_literals

# stdlib
import unittest
import pdb

# pyramid testing requirements
from pyramid import testing
from pyramid.exceptions import ConfigurationError
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.request import Request
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPSeeOther
import webob.cookies
import six
from webtest import TestApp

# ------------------------------------------------------------------------------

if False:
    from pyramid.session import SignedCookieSessionFactory

    my_session_factory = SignedCookieSessionFactory("itsaseekreet")
else:
    # Pyramid < 1.3:
    from pyramid.session import UnencryptedCookieSessionFactoryConfig  #

    my_session_factory = UnencryptedCookieSessionFactoryConfig(str("itsaseekreet"))


def start_session(request):
    request.session["i"] = 1


def increment_session(request):
    # just increment the session so we can keep track of flow
    if "i" not in request.session:
        request.session["i"] = 0
    request.session["i"] += 1


def check_session(request, expected):
    found = request.session.get("i")
    if found != expected:
        raise ValueError("expected %s ; got %s" % (expected, found))


def parse_session_cookie(response, via_webtest=None):
    # _cookies = [i for i in webob.cookies.parse_cookie(response.headers["set-cookie"])]
    # cache = dict((d(k), d(v)) for k, v in webob.cookies.parse_cookie(response.headers["set-cookie"]))
    try:
        _cookie = webob.cookies.Cookie(input=response.headers["set-cookie"])["session"]
        _cookie = "%s=%s" % (_cookie.name, _cookie.value)
        if not via_webtest:
            if isinstance(_cookie, unicode):
                _cookie = _cookie.encode()
            return _cookie
        return _cookie
    except Exception as exc:
        # no cookie
        return None


def _cookie_set(
    response,
    name,
    value="",
    max_age=None,
    path="/",
    domain=None,
    httponly=False,
    secure=False,
):
    # abstract and consolidate the pyramid `set_cookie` function
    # set_cookie(name, value='', max_age=None, path='/', domain=None, secure=False, httponly=False, comment=None, expires=None, overwrite=False)
    value = str(value)
    response.set_cookie(
        name,
        value=value,
        max_age=max_age,
        path=path,
        domain=domain,
        secure=secure,
        httponly=httponly,
    )


def parse_responsecallback_serverside(request):
    try:
        return int(request.headers["cookie"].split("=")[1])
    except Exception as exc:
        return None


def start_responsecallback(request):
    def _set(request, response):
        _cookie_set(response, "responsecallback", value=1)

    request.add_response_callback(_set)


def increment_responsecallback(request):
    # just increment the session so we can keep track of flow
    found = parse_responsecallback_serverside(request) or 0
    found += 1

    def _set(request, response):
        _cookie_set(response, "responsecallback", value=found)

    request.add_response_callback(_set)


def check_responsecallback(request, expected):
    found = parse_responsecallback_serverside(request) or 0
    if found != expected:
        raise ValueError("expected %s ; got %s" % (expected, found))


def parse_responsecallback_cookie(response, via_webtest=None):
    # _cookies = [i for i in webob.cookies.parse_cookie(response.headers["set-cookie"])]
    # cache = dict((d(k), d(v)) for k, v in webob.cookies.parse_cookie(response.headers["set-cookie"]))
    try:
        _cookie = webob.cookies.Cookie(input=response.headers["set-cookie"])[
            "responsecallback"
        ]
        _cookie = "%s=%s" % (_cookie.name, _cookie.value)
        if not via_webtest:
            if isinstance(_cookie, unicode):
                _cookie = _cookie.encode()
            return _cookie
        return _cookie
    except Exception as exc:
        # no cookie
        return None


def encode_headers_tween_factory(handler, registry):
    # PY2/3 testing compat
    # remove when PY2 support EOL
    # this is just used to handle `from __future__ import unicode_literals`
    def encode_headers_tween(request):
        resp = handler(request)
        for key in resp.headers.keys():
            values = resp.headers.getall(key)
            del resp.headers[key]
            for value in values:
                resp.headers.add(str(key), str(value))
        return resp

    return encode_headers_tween


def _ok_response():
    return Response(
        "<html><head></head><body>OK</body></html>", content_type="text/html"
    )


def view_session_init(request):
    start_session(request)
    return _ok_response()


def view_session_expect_1(request):
    check_session(request, 1)
    return _ok_response()


def view_session_expect_2(request):
    check_session(request, 2)
    return _ok_response()


def view_session_expect_3(request):
    check_session(request, 3)
    return _ok_response()


def view_session_HTTPSeeOther_return(request):
    increment_session(request)
    # redirect to self
    return HTTPSeeOther(location="/session/HTTPSeeOther/return")


def view_session_HTTPSeeOther_raise(request):
    increment_session(request)
    # redirect to self
    raise HTTPSeeOther(location="/session/HTTPSeeOther/raise")


class ViewSessionClass_HTTPSeeOther_raise(object):
    def __init__(self, request):
        self.request = request
        increment_session(request)
        raise HTTPSeeOther(location="/session/class/HTTPSeeOther/raise")

    def view(self):
        pass


def view_responsecallback_init(request):
    start_responsecallback(request)
    return _ok_response()


def view_responsecallback_expect_1(request):
    check_responsecallback(request, 1)
    return _ok_response()


def view_responsecallback_expect_2(request):
    check_responsecallback(request, 2)
    return _ok_response()


def view_responsecallback_expect_3(request):
    check_responsecallback(request, 3)
    return _ok_response()


def view_responsecallback_HTTPSeeOther_return(request):
    increment_responsecallback(request)
    # redirect to self
    return HTTPSeeOther(location="/responsecallback/HTTPSeeOther/return")


def view_responsecallback_HTTPSeeOther_raise(request):
    increment_responsecallback(request)
    # redirect to self
    raise HTTPSeeOther(location="/responsecallback/HTTPSeeOther/raise")


class ViewResponseCallbackClass_HTTPSeeOther_raise(object):
    def __init__(self, request):
        self.request = request
        increment_responsecallback(request)
        raise HTTPSeeOther(location="/responsecallback/class/HTTPSeeOther/raise")

    def view(self):
        pass


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""

    config = Configurator(settings=settings)
    config.add_tween(".encode_headers_tween_factory")  # PY2/3 testing compat

    config.set_session_factory(my_session_factory)

    #
    # Session Test Routes
    #
    config.add_route("view_session_init", "/session")
    config.add_view(view_session_init, route_name="view_session_init")

    config.add_route("view_session_HTTPSeeOther_return", "/session/HTTPSeeOther/return")
    config.add_view(
        view_session_HTTPSeeOther_return, route_name="view_session_HTTPSeeOther_return"
    )

    config.add_route("view_session_HTTPSeeOther_raise", "/session/HTTPSeeOther/raise")
    config.add_view(
        view_session_HTTPSeeOther_raise, route_name="view_session_HTTPSeeOther_raise"
    )
    config.add_route(
        "view_sessionclass_HTTPSeeOther_raise", "/session/class/HTTPSeeOther/raise"
    )
    config.add_view(
        ViewSessionClass_HTTPSeeOther_raise,
        attr="view",
        route_name="view_sessionclass_HTTPSeeOther_raise",
    )

    config.add_route("view_session_expect_1", "/session/expect/1")
    config.add_view(view_session_expect_1, route_name="view_session_expect_1")

    config.add_route("view_session_expect_2", "/session/expect/2")
    config.add_view(view_session_expect_2, route_name="view_session_expect_2")

    config.add_route("view_session_expect_3", "/session/expect/3")
    config.add_view(view_session_expect_3, route_name="view_session_expect_3")

    #
    # ResponseCallback Test Routes
    #
    config.add_route("view_responsecallback_init", "/responsecallback")
    config.add_view(view_responsecallback_init, route_name="view_responsecallback_init")

    config.add_route(
        "view_responsecallback_HTTPSeeOther_return",
        "/responsecallback/HTTPSeeOther/return",
    )
    config.add_view(
        view_responsecallback_HTTPSeeOther_return,
        route_name="view_responsecallback_HTTPSeeOther_return",
    )

    config.add_route(
        "view_responsecallback_HTTPSeeOther_raise",
        "/responsecallback/HTTPSeeOther/raise",
    )
    config.add_view(
        view_responsecallback_HTTPSeeOther_raise,
        route_name="view_responsecallback_HTTPSeeOther_raise",
    )

    config.add_route(
        "view_responsecallbackclass_HTTPSeeOther_raise",
        "/responsecallback/class/HTTPSeeOther/raise",
    )
    config.add_view(
        ViewResponseCallbackClass_HTTPSeeOther_raise,
        attr="view",
        route_name="view_responsecallbackclass_HTTPSeeOther_raise",
    )

    config.add_route("view_responsecallback_expect_1", "/responsecallback/expect/1")
    config.add_view(
        view_responsecallback_expect_1, route_name="view_responsecallback_expect_1"
    )

    config.add_route("view_responsecallback_expect_2", "/responsecallback/expect/2")
    config.add_view(
        view_responsecallback_expect_2, route_name="view_responsecallback_expect_2"
    )

    config.add_route("view_responsecallback_expect_3", "/responsecallback/expect/3")
    config.add_view(
        view_responsecallback_expect_3, route_name="view_responsecallback_expect_3"
    )

    if global_config.get("pyramid_subscribers_cookiexfer"):
        config.include("pyramid_subscribers_cookiexfer")

    return config.make_wsgi_app()


class _Test_Core(object):
    _configure = False
    _settings = None
    test_env = None

    def setUp(self):

        global_config = {
            "pyramid_subscribers_cookiexfer": self._configure,
        }
        if self._configure:
            app_settings = self._settings
        else:
            app_settings = {}
        app = main(global_config, **app_settings)
        self.test_env = {
            "wsgi.url_scheme": "https",
            "HTTP_HOST": "example.com",
        }
        self.testapp_app = TestApp(app)

    def tearDown(self):
        testing.tearDown()


class _Test_Session(_Test_Core):
    def test_session_def(self):
        # make a request that will start us off at 0 and increment to 1
        resp1 = self.testapp_app.get("/session", status=200)
        cookie1 = parse_session_cookie(resp1)

        # make a request to check a value of 1
        resp2 = self.testapp_app.get(
            "/session/expect/1", headers={"Cookie": cookie1}, status=200
        )
        cookie2 = (
            parse_session_cookie(resp2) or cookie1
        )  # might not return a new cookie

        # make a request to increment from 1 to 2
        resp3 = self.testapp_app.get(
            "/session/HTTPSeeOther/return", headers={"Cookie": cookie2}, status=303
        )
        cookie3 = parse_session_cookie(resp3)  # this better return a cookie
        assert cookie3 is not None

        # make a request to check a value of 2
        resp4 = self.testapp_app.get(
            "/session/expect/2", headers={"Cookie": cookie3}, status=200
        )
        cookie4 = (
            parse_session_cookie(resp4) or cookie3
        )  # might not return a new cookie

        # make a request to increment from 2 to 3
        resp5 = self.testapp_app.get(
            "/session/HTTPSeeOther/raise", headers={"Cookie": cookie4}, status=303
        )
        cookie5 = parse_session_cookie(resp5)  # this better return a cookie

        assert cookie5 is not None
        # make a request to check a value of 3
        resp6 = self.testapp_app.get(
            "/session/expect/3", headers={"Cookie": cookie5}, status=200
        )
        cookie6 = (
            parse_session_cookie(resp4) or cookie5
        )  # might not return a new cookie

    def test_session_class(self):
        # make a request that will start us off at 0 and increment to 1
        resp1 = self.testapp_app.get("/session", status=200)
        cookie1 = parse_session_cookie(resp1)

        # make a request to check a value of 1
        resp2 = self.testapp_app.get(
            "/session/expect/1", headers={"Cookie": cookie1}, status=200
        )
        cookie2 = (
            parse_session_cookie(resp2) or cookie1
        )  # might not return a new cookie

        # make a request to increment from 2 to 3
        resp3 = self.testapp_app.get(
            "/session/class/HTTPSeeOther/raise", headers={"Cookie": cookie2}, status=303
        )
        cookie3 = parse_session_cookie(resp3)  # this better return a cookie

        resp4 = self.testapp_app.get(
            "/session/expect/2", headers={"Cookie": cookie3}, status=200
        )
        cookie4 = (
            parse_session_cookie(resp4) or cookie3
        )  # might not return a new cookie


class Test_Session_Configured(_Test_Session, unittest.TestCase):
    _configure = True
    _settings = {
        "cookie_xfer.redirect_add_headers": True,
        "cookie_xfer.redirect_session_save": False,
        "cookie_xfer.apply_unique": False,
        "cookie_xfer.re_excludes": "^/(css|img|js|deform|_debug_toolbar)",
    }


class Test_Session_NotConfigured(_Test_Session, unittest.TestCase):
    _configure = False


class _Test_ResponseCallback(_Test_Core):
    def test_responsecallback_def(self):
        # make a request that will start us off at 0 and increment to 1
        resp1 = self.testapp_app.get("/responsecallback", status=200)
        cookie1 = parse_responsecallback_cookie(resp1)

        # make a request to check a value of 1
        resp2 = self.testapp_app.get(
            "/responsecallback/expect/1", headers={"Cookie": cookie1}, status=200
        )
        cookie2 = (
            parse_responsecallback_cookie(resp2) or cookie1
        )  # might not return a new cookie

        # make a request to increment from 1 to 2
        resp3 = self.testapp_app.get(
            "/responsecallback/HTTPSeeOther/return",
            headers={"Cookie": cookie2},
            status=303,
        )
        cookie3 = parse_responsecallback_cookie(resp3)  # this better return a cookie
        assert cookie3 is not None

        # make a request to check a value of 2
        resp4 = self.testapp_app.get(
            "/responsecallback/expect/2", headers={"Cookie": cookie3}, status=200
        )
        cookie4 = (
            parse_responsecallback_cookie(resp4) or cookie3
        )  # might not return a new cookie

        # make a request to increment from 2 to 3
        resp5 = self.testapp_app.get(
            "/responsecallback/HTTPSeeOther/raise",
            headers={"Cookie": cookie4},
            status=303,
        )
        cookie5 = parse_responsecallback_cookie(resp5)  # this better return a cookie

        assert cookie5 is not None
        # make a request to check a value of 3
        resp6 = self.testapp_app.get(
            "/responsecallback/expect/3", headers={"Cookie": cookie5}, status=200
        )
        cookie6 = (
            parse_responsecallback_cookie(resp4) or cookie5
        )  # might not return a new cookie

    def test_responsecallback_class(self):
        # make a request that will start us off at 0 and increment to 1
        resp1 = self.testapp_app.get("/responsecallback", status=200)
        cookie1 = parse_responsecallback_cookie(resp1)

        # make a request to check a value of 1
        resp2 = self.testapp_app.get(
            "/responsecallback/expect/1", headers={"Cookie": cookie1}, status=200
        )
        cookie2 = (
            parse_responsecallback_cookie(resp2) or cookie1
        )  # might not return a new cookie

        # make a request to increment from 2 to 3
        resp3 = self.testapp_app.get(
            "/responsecallback/class/HTTPSeeOther/raise",
            headers={"Cookie": cookie2},
            status=303,
        )
        cookie3 = parse_responsecallback_cookie(resp3)
        self.assertTrue(cookie3)
        resp4 = self.testapp_app.get(
            "/responsecallback/expect/2", headers={"Cookie": cookie3}, status=200
        )
        cookie4 = (
            parse_responsecallback_cookie(resp4) or cookie3
        )  # might not return a new cookie


class Test_ResponseCallback_Configured(_Test_ResponseCallback, unittest.TestCase):
    _configure = True
    _settings = {
        "cookie_xfer.redirect_add_headers": True,
        "cookie_xfer.redirect_session_save": False,
        "cookie_xfer.apply_unique": False,
        "cookie_xfer.re_excludes": "^/(css|img|js|deform|_debug_toolbar)",
    }


class Test_ResponseCallback_NotConfigured(_Test_ResponseCallback, unittest.TestCase):
    _configure = False
