import datetime
import time
import re
import urllib
from django import template
from django.conf import settings
from django.utils.dateformat import DateFormat

from newsutils import utils
from newsutils.utils import publish2
from newsutils.utils.bitly import Bitly

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
        

class Publish2Node(template.Node):
    def __init__(self, func, name, topic=None, count=5, var_name=None):
        self.func = getattr(publish2, func)
        self.name = template.Variable(name)
        
        if topic:
            self.topic = template.Variable(topic)
        else:
            self.topic = None
        
        self.count = count
        self.var_name = var_name
    
    
    def render(self, context):
        name = self.name.resolve(context)
        if self.topic:
            topic = self.topic.resolve(context)
        else:
            topic = None
        
        feed = self.func(name, topic)
        links = feed.items[:self.count]
        if self.var_name:
            context[self.var_name] = links
            return ''
        
        # this is really just for debugging
        return [str(i) for i in links]


class BitlyNode(template.Node):
    def __init__(self, long_url, var_name=None):
        self.long_url = template.Variable(long_url)
        self.var_name = var_name
    
    
    def render(self, context):
        bitly = Bitly(settings.BITLY_LOGIN, settings.BITLY_API_KEY)
        long_url = self.long_url.resolve(context)
        short_url = bitly.shorten(long_url)
        if self.var_name:
            context[var_name] = short_url
            return ''
        return short_url


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


@register.tag("publish2")
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
    if len(bits) > 6:
        raise template.TemplateSyntaxError("%s takes up to 5 args, %i given." % (bits[0]), len(bits))
    func = bits[1]
    name = bits[2]
    args = iter(bits[3:])
    
    var_name = topic = None
    count = 5
    
    for arg in args:
        if arg == 'as':
            var_name = args.next()
        elif arg.isdigit():
            count = int(arg)
        else:
            topic = arg
    
    return Publish2Node(func=func, name=name, topic=topic, count=count, var_name=var_name)


@register.tag("bitly")
def do_bitly(parser, token):
    """
    Simple tag for making long urls shorter
    
    Just shorten a URL:
    
        {% bitly "http://www.chrisamico.com/blog" %}
    
    Or, save the result as a variable (to cut down on repeated API calls):
    
        {% bitly "http://chrisamico.com/blog" as my_blog %}
    """
    bits = token.split_contents()
    if len(bits) == 2:
        return BitlyNode(bits[1])
    elif len(bits) == 4 and bits[2] == 'as':
        return BitlyNode(bits[1], bits[3])
    else:
        raise template.TemplateSyntaxError("%s takes 1 or 3 arguments. %s given" % (bits[0], len(bits)))

# filters

@register.filter('parsedate')
def parsedate(value, format=None):
    """
    Parses a date-like string into a Python datetime object,
    with an optional format argument, which follows Django's
    DateFormat, like the built-in date filter.
    """
    import dateutil.parser
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
    

