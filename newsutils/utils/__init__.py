import urllib, urllib2
import dateutil.parser

try:
    import simplejson as json
except ImportError:
    from django.utils import simplejson as json

from django.conf import settings

DEFAULT_HTTP_HEADERS = {
    "User-Agent": "django-newsutils",
    "Referer": None
}

if 'django.contrib.sites' in settings.INSTALLED_APPS:
    try:
        from django.contrib.sites.models import Site
        DEFAULT_HTTP_HEADERS['Referer'] = Site.objects.get_current().domain
    except: # It's possible you haven't installed the db tables yet, or won't
        DEFAULT_HTTP_HEADERS['Referer'] = getattr(settings, 'HTTP_REFERER', None)


def getjson(url, headers=None):
    if headers:
        headers = DEFAULT_HTTP_HEADERS.update(headers)
    else:
        headers = DEFAULT_HTTP_HEADERS.copy()
        
    request = urllib2.Request(url, headers=headers)
    return json.load(urllib2.urlopen(request))


def parsedate(s):
    """
    Convert a string into a (local, naive) datetime object.
    """
    dt = dateutil.parser.parse(s)
    if dt.tzinfo:
        dt = dt.astimezone(dateutil.tz.tzlocal()).replace(tzinfo=None)
    return dt
