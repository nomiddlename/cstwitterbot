import unittest
from mock import Mock
from cstwitterbot import BitlyCredentials
from cstwitterbot import BitlyShortener
from google.appengine.api import urlfetch

class BitlyShortenerTest (unittest.TestCase):
  def test_shorten(self):
    response = Mock()
    response.status_code = 200
    response.content = "{ \"errorCode\": 0, \"errorMessage\": \"\", \"results\": { \"http://cnn.com\": { \"hash\": \"31IqMl\", \"shortKeywordUrl\": \"\", \"shortUrl\": \"http://bit.ly/15DlK\", \"userHash\": \"15DlK\" } }, \"statusCode\": \"OK\" }"
    fetcher = Mock({"fetch": response}, urlfetch)
    credentials = BitlyCredentials(username="username", apikey="apikey")
    
    shortener = BitlyShortener(fetcher, credentials)
    short_url = shortener.shorten("http://cnn.com")
    self.assertEquals("http://bit.ly/15DlK", short_url)
    fetcher.mockCheckCall(0, "fetch", "http://api.bit.ly/shorten?version=2.0.1&longUrl=http://cnn.com&login=username&apikey=apikey", None, urlfetch.GET, None)
