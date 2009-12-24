import urllib
from newsutils import utils

BASE_URL = "http://api.bit.ly/"


class BitlyError(Exception):
    "Exception for Bitly"
    pass


class Bitly(object):
    """
    A simple bit.ly client:
    
    >>> from newsutils.utils.bitly import Bitly
    >>> bitly = Bitly(USERNAME, API_KEY)
    >>> bitly.shorten('http://www.chrisamico.com/blog')
    u'http://bit.ly/6UKhpv'
    """
    def __init__(self, username, api_key, method=None):
        self.username = username
        self.api_key = api_key
    
    
    def __repr__(self):
        return "<Bitly: %s>" % self.username
    
        
    def _apicall(self, method, **params):
        params['login'] = self.username
        params['apiKey'] = self.api_key
        params['version'] = '2.0.1'
        params['format'] = 'json'
        url = BASE_URL + method + '?' + urllib.urlencode(params)
        return utils.getjson(url)
    
    
    def shorten(self, long_url):
        response = self._apicall(method='shorten', longUrl=long_url)
        if response.get('statusCode', '') == 'ERROR':
            raise BitlyError(results['errorMessage'])
        return response['results'][long_url]['shortUrl']