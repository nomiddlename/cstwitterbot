import unittest
import base64
from mock import Mock
from cstwitterbot import TwitterClient
from cstwitterbot import TwitterCredentials
from google.appengine.api import urlfetch

class TwitterClientTest (unittest.TestCase):
  
  client = None
  fetcher = None
      
  def setUp(self):
    response = Mock()
    response.status_code = 200
    response.content = "[{ \"cheese\": \"biscuits\" }]"
    
    credentials = TwitterCredentials(username="csausbot", password="testing")
    self.fetcher = Mock({"fetch": response}, urlfetch)
    self.client = TwitterClient(self.fetcher, credentials)
    
  def testCredentials(self):
    authorization = self.client.headers['Authorization']
    self.assert_( authorization.startswith("Basic ") )
    self.assertEqual(authorization[6:], base64.encodestring("%s:%s" %("csausbot", "testing"))[:-1])
    
  def testMentionsWithoutLastStatus(self):
    mentions = self.client.mentions()
    self.fetcher.mockCheckCall(0, "fetch", "http://twitter.com/statuses/mentions.json", None, urlfetch.GET, self.client.headers)
    self.assertEqual(mentions[0]['cheese'], "biscuits")
    
  def testMentionsSinceLastStatus(self):
    mentions = self.client.mentions(1234)
    self.fetcher.mockCheckCall(0, "fetch", "http://twitter.com/statuses/mentions.json?since_id=1234", None, urlfetch.GET, self.client.headers)
    self.assertEqual(mentions[0]['cheese'], "biscuits")    
    
  def testReply(self):
    self.client.reply("statusid", "username", "reply text")
    self.fetcher.mockCheckCall(0, "fetch", "http://twitter.com/statuses/update.json?status=%40username%20reply%20text&in_reply_to_status_id=statusid", None, urlfetch.POST, self.client.headers)
