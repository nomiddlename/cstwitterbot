#!/usr/bin/env python
#

import wsgiref.handlers
import cstwitterbot
import os
import logging

from google.appengine.api.labs import taskqueue
from google.appengine.ext.db import BadValueError
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import urlfetch

class SetupHandler(webapp.RequestHandler):
	def get(self):
		credentials = cstwitterbot.TwitterCredentials.all().get()
		if self.request.path == "/setup/clear" and credentials:
			credentials.delete()
			credentials = None
			
		path = os.path.join(os.path.dirname(__file__), 'setup.html')
		self.response.out.write(template.render(path, { "credentials": credentials }))
		
	def post(self):
		credentials = cstwitterbot.TwitterCredentials.all().get()
		user = self.request.get('username')
		pw = self.request.get('password')
		error = None
		try:
			if credentials:
				credentials.username = self.request.get('username')
				credentials.password = self.request.get('password')
			else:
				credentials = cstwitterbot.TwitterCredentials(username=user, password=pw)
			credentials.put()
		except BadValueError, detail:
			logging.error("Problem with twitter credentials: %s", detail)
			error = "You have to specify a username and password."
			
		template_values = { "credentials": credentials, "error": error }
		path = os.path.join(os.path.dirname(__file__), 'setup.html')
		self.response.out.write(template.render(path, template_values))		

class BitlySetupHandler(webapp.RequestHandler):
	def get(self):
		credentials = cstwitterbot.BitlyCredentials.all().get()
		if self.request.path == "/setup/bitly/clear" and credentials:
			credentials.delete()
			credentials = None
			
		path = os.path.join(os.path.dirname(__file__), 'bitly.html')
		self.response.out.write(template.render(path, { "credentials": credentials }))
		
	def post(self):
		credentials = cstwitterbot.BitlyCredentials.all().get()
		user = self.request.get('username')
		apikey = self.request.get('apikey')
		error = None
		try:
			if credentials:
				credentials.username = self.request.get('username')
				credentials.apikey = self.request.get('apikey')
			else:
				credentials = cstwitterbot.BitlyCredentials(username=user, apikey=apikey)
			credentials.put()
		except BadValueError, detail:
			logging.error("Problem with bitly credentials: %s", detail)
			error = "You have to specify a username and apikey."
			
		template_values = { "credentials": credentials, "error": error }
		path = os.path.join(os.path.dirname(__file__), 'bitly.html')
		self.response.out.write(template.render(path, template_values))		
	
class ListenHandler(webapp.RequestHandler):
	
	def get(self):
		listener = self.setup_listener()
		if listener:
			listener.listen()
	
	def setup_listener(self):
		listener = None
		twitter_credentials = cstwitterbot.TwitterCredentials.all().get()
		if twitter_credentials:
			client = cstwitterbot.TwitterClient(urlfetch, twitter_credentials)
			twitterbot = cstwitterbot.TwitterBot(client, None, None)
			listener = cstwitterbot.Listener(twitterbot, taskqueue)
			
		return listener

class AnswerHandler(webapp.RequestHandler):
	
	def post(self):
		answerer = self.setup_answerer()
		if answerer:
			answerer.answer(self.request.get("question"))
		
	def setup_answerer(self):
		answerer = None
		twitter_credentials = cstwitterbot.TwitterCredentials.all().get()
		if twitter_credentials:
			client = cstwitterbot.TwitterClient(urlfetch, twitter_credentials)
			shortener = None
			bitly_credentials = cstwitterbot.BitlyCredentials.all().get()
			if bitly_credentials:
				shortener = cstwitterbot.BitlyShortener(urlfetch, bitly_credentials)
			twitterbot = cstwitterbot.TwitterBot(client, cstwitterbot.CitysearchOracle(), shortener)
			answerer = cstwitterbot.Answerer(twitterbot)
			
		return answerer
	
def main():
	application = webapp.WSGIApplication(
	[
	('/setup', SetupHandler),
	('/setup/clear', SetupHandler),
	('/setup/bitly', BitlySetupHandler),
	('/setup/bitly/clear', BitlySetupHandler),
	('/listen', ListenHandler),
	('/answer', AnswerHandler)
	],
	debug=True)
	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
