import datetime
import time
import re
import urllib
from django import template
from django.conf import settings

from newsutils import utils
from newsutils.utils import publish2

register = template.Library()

# tags

class GoogleNewsNode(template.Node):
    def __init__(self, query, var_name=None):
        self.query = template.Variable(query)
        self.var_name = var_name
    
    def render(self, context):
        base_url = 'http://ajax.googleapis.com/ajax/services/search/news?'
        self.query.resolve(context)
        params = {
            'v': '1.0',
            'rsz': 'large', # get 8 results
            'q': self.query
        }
        if hasattr(settings, "GOOGLE_API_KEY"):
            params['key'] = settings.GOOGLE_API_KEY
        
        url = base_url + urllib.urlencode(params)
        results = utils.getjson(url)['responseData']['results']
        
        if self.var_name:
            context[self.var_name] = results
            return ''
        
        return results
        


@register.tag("google_news")
def do_google_news(parser, token):
    """
    Get a Google News feed for a given query.
    Optional: Specify a count and save the result in a variable.
    
    Basic usage:
    
        {% google_news "Barack Obama" %}
        
    Save it as a variable:
    
        {% google_news "Barack Obama" as obama_news %}
        
    """    
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        msg = "%s takes at least one argument" % token.split_contents()[0]
        raise template.TemplateSyntaxError(msg)
        
    m = re.search(r'(.*?) as (\w+)', args)
    if m:
        query, var_name = m.groups()
        return GoogleNewsNode(query, var_name)
    else:
        return GoogleNewsNode(args)


def do_publish2(parser, token):
    """
    A template tag interface to Publish2.
    The tag gets recent links for journalists or newsgroups.
    
    Usage:
    
    {% publish2 get_for_journalist "Chris Amico" "politics" 5 as my_politics_links %}
    
    Or,
    
    {% publish2 get_for_newsgroup "NewsHour" 10 as newshour_links %}
    
    Arguments:
        - a publish2 function
        - a username or newsgroup name, depending on which function is called
        - an optional topic
        - a number of links to get (technically optional, but the default is 100)
        - an optional variable name to store the results in
        
    """
    bits = token.split_contents()
    func = bits[1]
    args = bits[2:]
    for arg in args:
        if arg == 'as':
            varname = arg.next()
        elif arg.isdigit():
            count = int(arg)


# filters

@register.filter('parsedate')
def parsedate(value, format=None):
    """
    Parses a date-like string into a Python datetime object,
    with an optional format argument, which follows Django's
    DateFormat, like the built-in date filter.
    """
    import dateutil.parser
    from django.utils.dateformat import DateFormat
    dt = dateutil.parser.parse(value)
    if format:
        return DateFormat(dt).format(format)
    return dt


@register.filter
def datetime_from_tuple(value, format=None):
    """
    Makes a time tuple into a real python datetime object.
    
    This is primarily a convenience filter for working with Feedparser
    """
    stamp = time.mktime(value)
    dt = datetime.datetime.fromtimestamp(stamp)
    if format:
        return DateFormat(dt).format(format)
    return dt
    

