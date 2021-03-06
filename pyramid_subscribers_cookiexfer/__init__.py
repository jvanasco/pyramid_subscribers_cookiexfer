import logging

log = logging.getLogger(__name__)

# stdlib
import re
import warnings

# pyramid
from pyramid.httpexceptions import HTTPException
from pyramid.settings import asbool


__VERSION__ = "0.2.0dev0"


# ------------------------------------------------------------------------------


def new_request(event):
    """
    new_request(event)

    :param event: Pyramid Event

    if there is a @cookie-xfer value in the session, will set the headers and then delete it
    """
    settings = event.request.registry.settings["@cookie_xfer"]
    if settings["re_excludes"] and re.match(
        settings["re_excludes"], event.request.path_info
    ):
        return
    log.debug("cookie-xfer cookiexfer_new_request")
    if settings["redirect_session_save"]:
        if "@cookie-xfer" in event.request.session:
            log.debug("cookie-xfer - migrating cookies FROM session")
            event.request.response.headers.extend(event.request.session["@cookie-xfer"])
            del event.request.session["@cookie-xfer"]


def new_response(event):
    """
    new_response(event) ; migrates headers or saves cookies.

    :param event: Pyramid Event

    NOTE you must either RETURN the exception, or RAISE it and include headers.
    """
    settings = event.request.registry.settings["@cookie_xfer"]
    if settings["re_excludes"] and re.match(
        settings["re_excludes"], event.request.path_info
    ):
        return

    if isinstance(event.response, HTTPException):
        log.debug("cookie-xfer cookiexfer_new_response")

        # cookies_request is populated if the exception is RETURNed
        # cookies_request is not populated if the exception is RAISEd from
        # a class based view during __init__ of the class.
        cookies_request = [
            (k, v)
            for (k, v) in event.request.response.headers.items()
            if k.lower() == "set-cookie"
        ]

        # cookies_response is populated if the exception is created with
        # headers specified
        cookies_response = [
            (k, v)
            for (k, v) in event.response.headers.items()
            if k.lower == "set-cookie"
        ]

        # debug
        # print "-------- cookies request  || %s" % cookies_request
        # print "-------- cookies response || %s" % cookies_response

        if cookies_request or cookies_response:
            log.debug("cookie-xfer - migrating cookies INTO session")

            # make a var stash
            headers_cookies_all = []
            headers_cookies_unique = []
            session_cookies_all = []
            session_cookies_unique = []

            # then precalculate how we'll save the cookies
            if not settings["apply_unique"]:
                # headers only need migrated cookies
                headers_cookies_all = cookies_request
                # session needs to save cookies
                session_cookies_all = cookies_request + cookies_response

            else:

                # do a 'seen' dict
                _cookies_unique__seen = {}

                # first we should favor the items that we specifically set
                # in the response
                # headers stay empty
                headers_cookies_unique = []
                # session should favor items from the resposne
                session_cookies_unique = cookies_response

                # and log them all as seen
                # don't add them to the cookies_unique, because they're already
                # in the object
                for (k, v) in cookies_response:
                    _v = v.split(";")
                    if _v[0] not in _cookies_unique__seen:
                        _cookies_unique__seen[_v[0]] = True

                # now add in new cookies
                for (k, v) in cookies_request:
                    _v = v.split(";")
                    if _v[0] not in _cookies_unique__seen:
                        _cookies_unique__seen[_v[0]] = True
                        headers_cookies_unique.append((k, v))
                        session_cookies_unique.append((k, v))

            # now start sending
            if settings["redirect_add_headers"]:
                if settings["apply_unique"]:
                    if headers_cookies_unique:
                        log.debug("headers_cookies_unique: %s", headers_cookies_unique)
                        event.response.headers.extend(headers_cookies_unique)
                else:
                    if headers_cookies_all:
                        log.debug("headers_cookies_all: %s", headers_cookies_all)
                        event.response.headers.extend(headers_cookies_all)

            if settings["redirect_session_save"]:
                if settings["apply_unique"]:
                    if session_cookies_unique:
                        log.debug("session_cookies_unique: %s", session_cookies_unique)
                        event.request.session["@cookie-xfer"] = session_cookies_unique
                else:
                    if session_cookies_all:
                        log.debug("session_cookies_all: %s", session_cookies_all)
                        event.request.session["@cookie-xfer"] = session_cookies_all

        log.debug("/cookie-xfer cookiexfer_new_response")


def includeme(config):
    """
    Previously `initialize_subscribers`
    """

    app_settings = config.registry.settings
    package_settings = {}

    for i in ("redirect_add_headers__unique", "redirect_session_save__unique"):
        if "cookie_xfer.%s" % i in app_settings:
            raise ValueError("`cookie_xfer.%s` was removed" % i)

    re_excludes = app_settings.get("cookie_xfer.re_excludes", None)
    if re_excludes:
        re_excludes = re.compile(re_excludes)
    package_settings["re_excludes"] = re_excludes

    for _setting in ("redirect_add_headers", "redirect_session_save", "apply_unique"):
        _app_key = "cookie_xfer.%s" % _setting
        _val = asbool(app_settings.get(_app_key, None))
        app_settings[_app_key] = _val
        package_settings[_setting] = _val

    # stash our package_settings
    config.registry.settings["@cookie_xfer"] = package_settings

    # add a NewResposne
    config.add_subscriber(new_response, "pyramid.events.NewResponse")

    # we only need a NewRequest subscriber if we're storing stuff in the session
    if package_settings["redirect_session_save"]:
        config.add_subscriber(new_request, "pyramid.events.NewRequest")
