import urllib2
from django.test import TestCase
from newsutils.utils import publish2

try:
    import json
except ImportError:
    import simplejson as json

class Publish2Test(TestCase):
    
    def _url_test(self, url, p2):
        result = json.load(urllib2.urlopen(url))
        
        self.assertEqual(len(result['items']), len(p2.items))
        
        for i, item in enumerate(result['items']):
            self.assertEqual(
                item['title'],
                p2.items[i].title
            )
    
    def test_empty_search(self):
        url = "http://www.publish2.com/search/links.json?"
        p2 = publish2.search()
        self._url_test(url, p2)
                
    def test_search_params(self):
        url = "http://www.publish2.com/search/links.json?tag=space"        
        p2 = publish2.search(tag='space')
        self._url_test(url, p2)
        
    def test_num_items(self):
        url = "http://www.publish2.com/search/links.json?number_of_items=37"
        p2 = publish2.search(count=37)
        self._url_test(url, p2)
    
    def test_query(self):
        url = "http://www.publish2.com/search/links.json?q=barack%20obama"
        p2 = publish2.search("Barack Obama")
        self._url_test(url, p2)
    
    def test_query_newsgroup(self):
        url = "http://www.publish2.com/search/links.json?q=Barack%20Obama&newsgroup=NewsHour"
        p2 = publish2.search("Barack Obama", "NewsHour")
        self._url_test(url, p2)
        
    def test_kitchen_sink(self):
        url = "http://www.publish2.com/search/links.json?tag=Media+%26+Journalism&newsgroup=Wired+Journalists+News&source=The+New+York+Times"
        p2 = publish2.search(
            tag = "Media & Journalism",
            newsgroup = "Wired Journalists News",
            source = "The New York Times"
        )
        self._url_test(url, p2)