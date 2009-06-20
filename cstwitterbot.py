import base64
import logging
import re
import urllib

from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from django.utils import simplejson

class TwitterClient:
  headers = {}
  fetcher = None
  
  def __init__(self, fetcher, username, password):
    self.fetcher = fetcher
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    self.headers = {'Authorization': "Basic %s" % base64string}
    
  def mentions(self, last_status_id = -1):
    mentions = []

    mention_url = "http://twitter.com/statuses/mentions.json"
    if last_status_id > 0:
      mention_url += "?since_id=%i" %(last_status_id)
      
    result = self.fetcher.fetch(mention_url, None, urlfetch.GET, self.headers)          
    if result.status_code != 200:
      logging.error("Problem at the twitter end, status code %i, response was: %s" %(result.status_code, result.content))
    else:
      mentions = simplejson.loads(result.content)
      
    return mentions
		
  def reply(self, status_id, username, reply_text):
    reply_url = "http://twitter.com/statuses/update.json?status=%s&in_reply_to_status_id=%s" %(urllib.quote("@"+username+" "+reply_text), urllib.quote(status_id))
    result = self.fetcher.fetch(reply_url, None, urlfetch.POST, self.headers)
    if result.status_code != 200:
      logging.error("Problem updating status, url was {%s}, status code %i, response was: %s" %(reply_url, result.status_code, result.content))

class TwitterBot:
  
  def __init__(self, client, oracle):
    self.client = client
    self.oracle = oracle
    
  def questions_since(self, last_question):
    last_mention = last_question.id if last_question else -1
    mentions = self.client.mentions(last_mention)
        
    questions = []
    for mention in mentions:
      question = Question(mention)
      if question.isValid():
        questions.append(question)
      
    return questions
    
  def answer(self, question):
    self.client.reply(question.id, question.asker, self.oracle.answer(question.data))
    
class Question:
  id = ""
  asker = ""
  data = ""
  
  def __init__(self, mention):
    if "id" in mention:
      self.id = mention['id']
    if "user" in mention and 'screen_name' in mention['user']:
      self.asker = mention['user']['screen_name']
    if "text" in mention:
      self.data = self.__clean(mention['text'])
    
  def __clean(self, text):
    cleaned = re.sub(r'^@.*?\s','', text).strip()
    return cleaned
    
  def isValid(self):
    return len(self.asker) > 0 and len(self.id) > 0 and len(self.data) > 0 and self.data.find("@") == -1
      
class ListenHandler(webapp.RequestHandler):

  def get(self):
    username = "csausbot"
    password = "chw1l10dd1n4s"
    self.response.headers['Content-Type'] = 'text/plain'
    url = "http://twitter.com/statuses/mentions.json"
    result = urlfetch.fetch(url, None, method=urlfetch.GET, headers=headers)
    
    if result.status_code != 200:
      self.response.out.write("Problem at the twitter end, response was: "+result.content)
      return
    else:
			mentions = simplejson.load(result.content)
      
    try:
			for mention in mentions:
				text = mention['text']
				id = mention['id']
				user = mention['user']['screen_name']
				self.response.out.write("Twitterer "+user+" said: "+text+" (id: "+id+")\n")
    except DeadlineExceededError:
			self.response.clear()
			self.response.set_status(500)
			self.response.out.write("This operation could not be completed in time...")
 	
