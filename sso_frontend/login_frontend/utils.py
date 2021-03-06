"""
Utility functions
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User as DjangoUser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from login_frontend.models import User, BrowserDetails, KeystrokeSequence, UserLocation
import datetime
import dateutil.parser
import geoip2
import geoip2.database
import geoip2.errors
import geoip2.models
import ipaddr
import logging
import json
import login_frontend._slumber_auth as _slumber_auth
import slumber
import time
import urllib
import pytz
import re
import os
import sys
import urlparse
from django_statsd.clients import statsd as sd

from django.core.cache import get_cache

dcache = get_cache("default")
user_cache = get_cache("users")
ucache = get_cache("user_mapping")
bcache = get_cache("browsers")

log = logging.getLogger(__name__)
timing_log = logging.getLogger("timing_data")

geo = geoip2.database.Reader(settings.GEOIP_DB)
IP_NETWORKS = settings.IP_NETWORKS


@sd.timer("login_frontend.utils.custom_log")
def custom_log(request, message, **kwargs):
    """ Automatically logs username, remote IP and bid_public """
    if request is None:
        log.warn("Skipping custom_log as request is None: %s", message)
        return
    try:
        raise Exception
    except:
        stack = sys.exc_info()[2].tb_frame.f_back
    if stack is not None:
        stack = stack.f_back
    while hasattr(stack, "f_code"):
        co = stack.f_code
        filename = os.path.normcase(co.co_filename)
        filename = co.co_filename
        lineno = stack.f_lineno
        co_name = co.co_name
        break

    level = kwargs.get("level", "info")
    method = getattr(log, level)
    remote_addr = request.remote_ip
    bid_public = username = ""
    if hasattr(request, "browser") and request.browser:
        bid_public = request.browser.bid_public
        if request.browser.user:
            username = request.browser.user.username
    method("[%s:%s:%s] %s - %s - %s - %s", filename, lineno, co_name,
                            remote_addr, username, bid_public, message)


__all__ = ["redir_to_sso", "is_private_net", "save_timing_data", "get_and_refresh_user", "refresh_user", "get_geoip_string", "redirect_with_get_params", "dedup_messages", "paginate", "get_return_url", "check_browser_name", "map_username", "get_ratelimit_keys"]


LOCAL_URLS = {
    "/sessions": "sessions page",
    "/configure": "settings page",
    "/index": "index page",
    "/idp/login": "SAML login",
    "/admin_": "admin UI",
}


def get_ratelimit_keys(request):
    keys = [request.META.get("REMOTE_ADDR")]
    if hasattr(request, "browser") and request.browser and request.browser.user:
        keys.append(request.browser.user.username)
    return keys

@sd.timer("login_frontend.utils.store_location")
def store_location_caching(request, location = None):
    r_k = "location-tmp-for-%s" % request.browser.bid_public
    if not request.browser.user:
        custom_log(request, "No signed-in user. Not storing location info: %s" % location, level="warn")
        bcache.set(r_k, location, 60*60)
        bcache.set(r_k+"-ip", request.remote_ip, 60*60)
        return HttpResponse("No signed-in user.")
    if not location:
        location = bcache.get(r_k)
        if location:
            custom_log(request, "Loaded location from redis")
            remote_ip = bcache.get(r_k+"-ip")
            bcache.delete_many([r_k, r_k+"-ip"])
    else:
        remote_ip = request.remote_ip
    if not isinstance(location, dict):
        return HttpResponse("Invalid data")

    if all (k in location for k in ("longitude", "latitude", "accuracy")):
        data = {}
        for k in ("longitude", "latitude", "altitude", "accuracy", "altitude_accuracy", "heading", "speed"):
            try:
                data[k] = float(location.get(k))
            except ValueError:
                data[k] = None
        data["bid_public"] = request.browser.bid_public
        data["remote_ip"] = remote_ip
        data["user"] = request.browser.user
        UserLocation.objects.create(**data)
        bcache.set("location-stored-for-%s-%s" % (request.browser.bid_public, request.browser.user.username), timezone.now(), 600)
        bcache.set("location-authorized-for-%s" % (request.browser.bid_public), True, 86400*7)
    else:
        custom_log(request, "Invalid store_location request: missing mandatory fields.", level="warn")
        return HttpResponse("Invalid request: missing mandatory fields")
    return HttpResponse("OK")

@sd.timer("login_frontend.utils.map_username")
def map_username(username):
    """ Maps user aliases to username """
    r_k = "email-to-username-%s" % username
    username_tmp = ucache.get(r_k)
    if username_tmp is not None:
        return username_tmp
    return username

@sd.timer("login_frontend.utils.get_return_url")
def get_return_url(request):
    try:
        if request.GET.get("next"):
            return_url = urllib.unquote(request.GET.get("next"))
            parsed = urlparse.urlparse(return_url)
            if parsed.path.startswith("/idp/login"):
                if parsed.query:
                    query_params = urlparse.parse_qs(parsed.query)
                    if "saml_id" in query_params:
                        return_info = dcache.get("saml-return-%s" % query_params["saml_id"][0])
                        if return_info:
                            return return_info

            if parsed.netloc == settings.FQDN or parsed.hostname is None: # absolute or relative URLs
                # Local URL
                for url in LOCAL_URLS:
                    if parsed.path.startswith(url):
                        return LOCAL_URLS[url]
                return "login service"
            elif return_url.startswith("/openid/"):
                params = urlparse.parse_qs(return_url)
                if "openid.return_to" in params:
                    parsed = urlparse.urlparse(params["openid.return_to"][0])
                    if parsed.netloc:
                        return parsed.netloc
                    return "unknown OpenID"

        elif request.GET.get("back"):
            return_url = request.GET.get("back")
            parsed = urlparse.urlparse(return_url)
            if parsed.netloc:
                return parsed.netloc
    except Exception, e:
        log.error("get_return_url failed with %s" % e)

    return None

INVALID_BROWSER_NAMES = (
    "...",
)

INVALID_BROWSER_RE = (
    re.compile(r"^(.)\1+$"), # disallow repeating single character
    re.compile(r"^(..)\1+$"), # 2
    re.compile(r".*asdf.*"),
    re.compile(r".*qwerty.*"),
    re.compile(r".*1234.*"),
    re.compile(r"^[0-9]*$"),
)

@sd.timer("login_frontend.utils.check_browser_name")
def check_browser_name(browser_name):
    browser_name = browser_name.lower()
    for pattern in INVALID_BROWSER_NAMES:
        if browser_name == pattern:
            return False
    for pattern in INVALID_BROWSER_RE:
        if pattern.match(browser_name):
            return False
    return True

@sd.timer("login_frontend.utils.dedup_messages")
def dedup_messages(request, level, message):
    storage = messages.get_messages(request)
    for amessage in storage:
        if unicode(amessage) == unicode(message):
            storage.used = False
            return False
    storage.used = False
    messages.add_message(request, level, message)

@sd.timer("login_frontend.utils.paginate")
def paginate(request, queryset, **kwargs):
    per_page = kwargs.get("per_page", 100)
    paginator = Paginator(queryset, per_page)
    page = request.GET.get("page")
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
        page = 1
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)
        page = paginator.num_pages
    entries.pagerange = range(max(1, entries.number - 5), min(paginator.num_pages, entries.number + 5))
    return entries


@sd.timer("login_frontend.utils.redir_to_sso")
def redir_to_sso(request, **kwargs):
    """ Returns HttpResponseRedirect to proper login service. """
    sso = request.GET.get("_sso")
    if sso == "pubtkt":
        log.debug("Redirecting with pubtkt")
        return redirect_with_get_params("login_frontend.providers.pubtkt", request.GET.dict())
    elif sso == "internal":
        log.debug("Redirecting with internal sso")
        return redirect_with_get_params("login_frontend.providers.internal_login", request.GET.dict())
    else:
        log.debug("No sso preference configured")
        if not kwargs.get("no_default", False):
            log.debug("Redirecting back to indexview")
            return redirect_with_get_params("login_frontend.views.indexview", request.GET.dict())
        log.debug("No default configured - return None")
        return None


@sd.timer("login_frontend.utils.is_private_net")
def is_private_net(ip_address):
    """ Returns description if specified in private networks, imported from
        local_settings """
    try:
        ip = ipaddr.IPv4Address(ip_address)
    except:
        return False

    for (network, _, _, description) in IP_NETWORKS:
        if ((isinstance(network, ipaddr.IPv4Address) and
            ip is network) or
           (isinstance(network, ipaddr.IPv4Network) and
            ip in network)):
            return description
    return False

@sd.timer("login_frontend.utils.save_timing_data")
def save_timing_data(request, user, timing_data):
    """ Saves timing data with username, UA and bid. """
    if not (hasattr(request, "browser") and request.browser):
        log.error("Missing request.browser on timing data input")
        return
    browser = request.browser
    user_agent = request.META.get("HTTP_USER_AGENT")
    bid_public = request.browser.bid_public
    username = user.username
    timing_log.info("%s - %s - %s - %s - %s" % (time.time(), username, user_agent, timing_data, bid_public))

    try:
        data = json.loads(timing_data)
    except (ValueError, EOFError):
        log.error("Unable to load timing data json")
        return

    if not isinstance(data, dict):
        log.error("Invalid timing data dictionary")

    resolution = data.get("resolution")
    remote_clock = data.get("browserclock")
    remote_clock_offset = remote_clock.get("timezoneoffset")
    remote_clock_time = remote_clock.get("utciso")

    plugins = data.get("plugins")

    performance = data.get("performance")
    performance_performance = performance_memory = performance_timing = performance_navigation = None
    if isinstance(performance, dict):
        performance_performance = performance.get("performance")
        performance_memory = performance.get("memory")
        performance_timing = performance.get("timing")
        performance_navigation = performance.get("navigation")

    BrowserDetails.objects.create(browser=browser, timestamp=timezone.now(), remote_clock_offset=str(remote_clock_offset), remote_clock_time=str(remote_clock_time), performance_performance=str(performance_performance), performance_memory=str(performance_memory), performance_timing=str(performance_timing), performance_navigation=str(performance_navigation), resolution=str(resolution), plugins=str(plugins))

    create_items = []

    if "id_username" in data:
        fieldname = KeystrokeSequence.USERNAME
        timing = str(data.get("id_username"))
        create_items.append((fieldname, timing))

    if "id_password" in data:
        fieldname = KeystrokeSequence.PASSWORD
        timing = str(data.get("id_password"))
        create_items.append((fieldname, timing))

    if "id_otp" in data:
        if request.path.startswith("/second/sms"):
            fieldname = KeystrokeSequence.OTP_SMS
        else:
            fieldname = KeystrokeSequence.OTP_AUTHENTICATOR
        timing = str(data.get("id_otp"))
        create_items.append((fieldname, timing))

    for fieldname, timing in create_items:
        KeystrokeSequence.objects.create(user=user, browser=browser, fieldname=fieldname, timing=timing, timestamp=timezone.now(), resolution=resolution, was_correct=True)



@sd.timer("login_frontend.utils.get_and_refresh_user")
def get_and_refresh_user(username): # pragma: no cover
    """ Loads and refreshes user information from LDAP """
    log.info("Refreshing %s" % username)
    api = slumber.API(settings.FUM_API_ENDPOINT, auth=_slumber_auth.TokenAuth(settings.FUM_ACCESS_TOKEN))
    refresh_user(api.users().get(username=username))

@sd.timer("login_frontend.utils.refresh_user")
def refresh_user(user): # pragma: no cover
    """ Refreshes user details, if necessary. """
    def parse_datetime(date_string):
        try:
            d = datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
        except (ValueError, TypeError):
            return None
        utc = pytz.timezone("UTC")
        return utc.localize(d)

    username = user.get("username")
    log.info("Updating %s" % username)
    first_name = user.get("first_name", "Unknown")
    last_name = user.get("last_name", "Unknown")
    email = user.get("email", "")
    phone1 = user.get("phone1")
    phone2 = user.get("phone2")

    password_changed = parse_datetime(user.get("password_changed_date"))
    password_expires = parse_datetime(user.get("password_expiration_date"))


    if username is None or email is None:
        log.debug("%s - %s - Username or email is none - skip" % (username, email))
        return
    if first_name is None:
        first_name = "Unknown"
    if last_name is None:
        last_name = "Unknown"

    for (k, v) in  (("first_name", first_name),
                    ("last_name", last_name),
                    ("email", email),
                    ("phone1", phone1),
                    ("phone2", phone2),
                    ("password_changed", password_changed),
                    ("password_expires", password_expires)):
        user_cache.set("%s-%s" % (username, k), v, 86400*14)
    user_cache.set(username, True, 86400*14)

    (user, created1) = DjangoUser.objects.get_or_create(username=username,
            defaults={"email": email, "is_staff": False, "is_active": True, "is_superuser": False, "last_login": timezone.now(), "date_joined": timezone.now()})
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.save()

    (obj, created2) = User.objects.get_or_create(username=username)

    obj.first_name = first_name
    obj.last_name = last_name

    obj.password_changed = password_changed
    obj.password_expires = password_expires

    changed = obj.refresh_strong(email, phone1, phone2, created=created2)
    if changed or created1 or created2:
        log.info("Changed or created new objects")
        return True

@sd.timer("login_frontend.utils.get_geoip_string")
def get_geoip_string(ip_address):
    """ Returns short location string for IP address. """
    private_net = is_private_net(ip_address)
    if private_net:
        return private_net
    try:
        data = geo.city(ip_address)
    except:
        return "Unknown"
    country = data.country.iso_code
    city = data.city.name
    if city is None:
        return "%s" % country
    return "%s (%s)" % (country, city)

@sd.timer("login_frontend.utils.redirect_with_get_params")
def redirect_with_get_params(url_name, get_params = None):
    """ Returns HttpResponseRedirect with query string. """
    url = reverse(url_name)
    if not get_params:
        return HttpResponseRedirect(url)
    params = urllib.urlencode(get_params)
    full_url = url + "?%s" % params
    log.debug("Redirecting to %s" % full_url)
    return HttpResponseRedirect(full_url)
