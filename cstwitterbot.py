import base64
import logging
import re
import urllib

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from django.utils import simplejson

class BitlyCredentials(db.Model):
  username = db.StringProperty(required=True)
  apikey = db.StringProperty(required=True)
  
class TwitterCredentials(db.Model):
  username = db.StringProperty(required=True)
  password = db.StringProperty(required=True)
  
class TwitterClient:
  headers = {}
  fetcher = None
  
  def __init__(self, fetcher, credentials):
    self.fetcher = fetcher
    base64string = base64.encodestring('%s:%s' % (credentials.username, credentials.password))[:-1]
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
  
  def __init__(self, client, oracle, shortener):
    self.client = client
    self.oracle = oracle
    self.shortener = shortener
    
  def questions_since(self, last_question):
    last_mention = last_question.id if last_question else -1
    mentions = self.client.mentions(last_mention)
        
    questions = []
    for mention in mentions:
      question = Question.from_mention(mention)
      if question:
        question.put()
        questions.append(question)
      
    return questions
    
  def answer(self, question):
    answer = self.oracle.answer(question.data)
    if self.shortener:
      answer = self.shortener.shorten(answer)
    self.client.reply(question.id, question.asker, answer)
    
class Question(db.Model):
  id = db.StringProperty(default="")
  asker = db.StringProperty(default="")
  data = db.StringProperty(default="")
  retrieved = db.DateTimeProperty(auto_now_add=True)
  answered = db.DateTimeProperty(auto_now=True)
  location = db.GeoPtProperty()
  
  def __cmp__(self, other):
    return cmp(self.id, other.id)
  
  def from_mention(mention):
    question = Question()
    if "id" in mention:
      question.id = mention['id']
    if "user" in mention and 'screen_name' in mention['user']:
      question.asker = mention['user']['screen_name']
    if "text" in mention:
      question.data = Question._clean(mention['text'])
      
    if not question.is_valid():
      question = None
      
    return question

  def _clean(text):
    cleaned = re.sub(r'^@.*?\s','', text).strip()
    return cleaned
    
  def last_question():
    query = Question.all()
    query.order("-retrieved")
    return query.get()
    
  from_mention = staticmethod(from_mention)
  _clean = staticmethod(_clean)
  last_question = staticmethod(last_question)
    
  def is_valid(self):
    return len(self.asker) > 0 and len(self.id) > 0 and len(self.data) > 0 and self.data.find("@") == -1
    
class CitysearchOracle:
  def answer(self, question):
    return "http://citysearch.com.au/search?keyword="+urllib.quote(question)
    
class BitlyShortener:
  def __init__(self, fetcher, credentials):
    self.fetcher = fetcher
    self.credentials = credentials
    
  def shorten(self, url_to_shorten):
    short_url = None

    api_shorten = "http://api.bit.ly/shorten?version=2.0.1&longUrl=%s&login=%s&apikey=%s" %(url_to_shorten, self.credentials.username, self.credentials.apikey)
    result = self.fetcher.fetch(api_shorten, None, urlfetch.GET, None)          
    if result.status_code != 200:
      logging.error("Problem at the bit.ly end, status code %i, response was: %s" %(result.status_code, result.content))
    else:
      api_response = simplejson.loads(result.content)

    short_url = api_response["results"][url_to_shorten]["shortUrl"]
    return short_url

class Listener:
  def __init__(self, twitterbot, queue):
    self.twitterbot = twitterbot
    self.queue = queue
    
  def listen(self):
    questions = self.twitterbot.questions_since(Question.last_question())
    for question in questions:
      self.queue.add(uri="/answer", params={ "question": question.id })

class Answerer:
  def __init__(self, twitterbot):
    self.twitterbot = twitterbot
    
  def answer(self, question_id):
    query = Question.all()
    query.filter("id = ", question_id)
    question = query.get()
    
    if question:
      logging.info("Answering question %r", question)
      self.twitterbot.answer(question)
      question.put()