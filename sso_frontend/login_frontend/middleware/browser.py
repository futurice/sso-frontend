#pylint: disable-msg=C0301

"""
Middleware classes.

BrowserMiddleware adds request.browser, and automatically signs user out,
if browser was restarted, and not saved.

Also, session cookie is automatically added if it does not exist yet.
"""

from django.conf import settings
from django.contrib import messages
from django.core.cache import get_cache
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import timezone
from django_statsd.clients import statsd as sd
from login_frontend.models import Browser, BrowserUsers, BrowserLogin, create_browser_uuid
from login_frontend.providers import pubtkt_logout
from login_frontend.utils import dedup_messages
import logging
import re

dcache = get_cache("default")

log = logging.getLogger(__name__)

DISALLOWED_UA = [
 re.compile("^Wget/.*"),
 re.compile("^Pingdom.com_bot_version.*"),
 re.compile("^curl/.*"),
 re.compile("^nutch-.*"),
]

__all__ = ["get_browser", "BrowserMiddleware", "get_browser_instance"]

@sd.timer("get_browser_instance")
def get_browser_instance(request):    
    bid = request.COOKIES.get(Browser.C_BID)
    if not bid:
        return None
    try:
        browser = Browser.objects.select_related("user").get(bid=bid)
        sd.incr("get_browser_instance.success", 1)
    except Browser.DoesNotExist:
        sd.incr("get_browser_instance.invalid", 1)
        log.info("Unknown browser id '%s' from '%s'", bid, request.remote_ip)
        return None

    return browser

@sd.timer("get_browser")
def get_browser(request):
    browser = get_browser_instance(request)
    if browser is None:
        return None
    bid = browser.bid_public

    if request.path.startswith("/csp-report") or request.path.startswith("/timesync"):
        log.debug("Browser '%s' from '%s' reporting CSP/timesync - skip sign-out processing", bid, request.remote_ip)
        sd.incr("get_browser.skip", 1)
        return browser

    if request.COOKIES.get(Browser.C_BID_SESSION) == browser.bid_session:
        browser.valid_session_bid = True
    else:
        browser.valid_session_bid = False
        # Mark session based logins as signed_out
        sessions = BrowserLogin.objects.filter(browser=browser).filter(expires_session=True).filter(signed_out=False)
        for session in sessions:
            log.info("Marking session %s for %s (user %s) as signed out, after browser session id cookie disappeared.", session.sso_provider, browser.bid, session.user.username)
            session.signed_out = True
            session.save()
        if not browser.save_browser:
            # Browser was restarted, and save_browser is not set. Logout.
            log.info("Browser bid_public=%s was restarted. Logging out. path: %s", browser.bid_public, request.path)
            sd.incr("get_browser.browser_restart", 1)
            dedup_messages(request, messages.INFO, "According to our records, your browser was restarted. Therefore, you were signed out. If this is your own computer, you can avoid this by checking 'Remember this browser' below the sign-in form.")
            browser.logout(request)

    if browser.user:
        r_k = "browser-location-last-update-%s-%s" % (browser.user.username, browser.bid_public)
        last_update = dcache.get(r_k)
        remote_address = request.remote_ip
        if last_update != remote_address:
            user_to_browser, _ = BrowserUsers.objects.get_or_create(user=browser.user, browser=browser)
            if request.path.startswith("/ping"):
                sd.incr("get_browser.passive_access", 1)
                user_to_browser.remote_ip_passive = remote_address
                user_to_browser.last_seen_passive = timezone.now()
            else:
                sd.incr("get_browser.active_access", 1)
                user_to_browser.remote_ip = remote_address
                user_to_browser.last_seen = timezone.now()
            user_to_browser.save()
            dcache.set(r_k, remote_address, 30)
    return browser

class BrowserMiddleware(object):
    """ Adds request.browser. """ 

    @sd.timer("BrowserMiddleware.process_request")
    def process_request(self, request):
        """ Adds request.browser. Filters out monitoring bots. """
        ua = request.META.get("HTTP_USER_AGENT")
        ret = {}
        if ua is None:
            return render_to_response("login_frontend/errors/you_are_a_bot.html", ret, context_instance=RequestContext(request))
        for ua_re in DISALLOWED_UA:
            if ua_re.match(ua):
                try:
                    (_, ret["admin"]) = settings.ADMINS[0]
                except (IndexError, ValueError):
                    pass
                return render_to_response("login_frontend/errors/you_are_a_bot.html", ret, context_instance=RequestContext(request))

        request.browser = get_browser(request)
        if hasattr(request, "browser") and request.browser and ua != request.browser.ua:
            request.browser.change_ua(request, ua)

    @sd.timer("BrowserMiddleware.process_response")
    def process_response(self, request, response):
        """ Automatically adds session cookie if old one is not available. """
        response["Server"] = "https://github.com/ojarva/sso-frontend"
        if request.path.startswith("/csp-report") or request.path.startswith("/timesync"):
            log.debug("Browser from '%s' reporting CSP/timesync - skip process_response", request.remote_ip)
            sd.incr("login_frontend.middleware.BrowserMiddleware.process_response.skip", 1)
            return response
        
        # Browser from process_request is not available here.
        browser = get_browser_instance(request)

        if not browser or browser.get_auth_level() < Browser.L_STRONG:
            response = pubtkt_logout(request, response)

        if not browser:
            log.debug("Browser does not exist")
            return response

        cookies = browser.get_cookies()
        if request.COOKIES.get(Browser.C_BID_SESSION) != browser.bid_session:
            # No valid session ID exists. Regen it first.
            browser.bid_session = create_browser_uuid()
            browser.save()
            log.info("Session bid does not exist. Regenerating. bid_public=%s, bid_session=%s" % (browser.bid_public, browser.bid_session))
            cookies = browser.get_cookies()

        if request.COOKIES.get(Browser.C_BID_PUBLIC) != browser.bid_public:
            # Public bid does not match. Set it again.
            cookies = browser.get_cookies()

        for cookie_name, cookie in cookies:
            log.debug("Setting cookie %s=%s for %s at %s" % (cookie_name, cookie, browser.bid_public, request.path))
            response.set_cookie(cookie_name, **cookie)
        return response