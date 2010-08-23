"""
A Python interface for Publish2

Publish2 is a collaborative bookmarking tool for journalists.
While it doesn't have an official API, but it does offer a 
filterable feed of links in JSON, XML and RSS.

The API, as it is, allows filtering on the following attributes:
 - tag
 - newgroup
 - source
 - date added
 - search query

The number of items returned defaults to 10, and can be set 
with the number_of_items query argument.

Each feed provides metadata on the journalist or newsgroup
submitting links. Each item lists a title, link, tags, publication,
date submitted, date published and public comment.

This is a modified version of the original stand-alone module.
Since it is part of Django-NewsUtils, it uses other parts of
Django where it makes life easier.
"""
import datetime
import urllib, urllib2
try:
    import json
except ImportError:
    import simplejson as json

from newsutils import utils

__all__ = ('Publish2Error', 'get_for_journalist', 'get_for_newsgroup')


class Publish2Error(Exception):
    "Exception for Publish2 errors"

BASE_URL = 'http://www.publish2.com/search/links.json?'

# results

class Publish2Object(object):
    "Base class for Publish2"
    def __init__(self, d):
        self.__dict__ = d
    
    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.__str__())

    def __str__(self):
        return ''


class Publish2Tag(Publish2Object):
    "A tag on a link"
    
    def __str__(self):
        return self.name


class Publish2Link(Publish2Object):
    "Link from a Publish2 feed"
        
    def __init__(self, d):
        self.__dict__ = d
        self.publication_date = utils.parsedate(d['publication_date'])
        self.created_date = utils.parsedate(d['created_date'])
        if hasattr(self, 'tags'):
            #tags = self.tags[0].values()
            self.tags = [Publish2Tag(t) for t in self.tags]
        else:
            self.tags = []
            
    def __str__(self):
        return self.title


class Publish2Feed(Publish2Object):
    "A feed of publish2 links"
    def __init__(self, d):
        self.__dict__ = d
        self.items = [Publish2Link(i) for i in getattr(self, 'items', [])]
        
    def __str__(self):
        return self.title


def search(q='', newsgroup='', tag='', source='', count=10, **kwargs):
    """
    Return a filtered Publish2 news feed
    """
    kwargs.update({
        'q': q,
        'newsgroup': newsgroup,
        'tag': tag,
        'source': source,
        'number_of_items': count,
    })
    url = BASE_URL + urllib.urlencode(kwargs)
    result = json.load(urllib2.urlopen(url))
    return Publish2Feed(result)




