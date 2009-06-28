import unittest
from mock import Mock
from cstwitterbot import TwitterBot
from cstwitterbot import Question
    
class TwitterBotTest (unittest.TestCase):
  def setUp(self):
    query = Question.all()
    query.filter('id = ','testid')
    for question in query:
      question.delete()
      
  def tearDown(self):
    query = Question.all()
    query.filter('id = ','testid')
    for question in query:
      question.delete()

  def testQuestions(self):
    test_mentions = [ 
      { "id" : "testid", "user": { "screen_name": "nomiddlename" }, "text": "@csausbot testing, testing, one, two, three."},
      { "id" : "testid", "user": { "screen_name": "cheekymonkey" }, "text": "@csausbot      "},
      { "id" : "testid", "user": { "screen_name": "eh" }, "text": "This @csausbot is really cool."}
      ]
    client = Mock({ "mentions": test_mentions })
    
    twitterbot = TwitterBot(client, None, None)
    questions = twitterbot.questions_since(None)
    client.mockCheckCall(0, "mentions", -1)
    
    self.assertEqual(len(questions), 1)
    question = questions[0]
    self.assertEqual(question.asker, "nomiddlename")
    self.assertEqual(question.data, "testing, testing, one, two, three.")
    
    query = Question.all()
    query.filter('id = ','testid')
    self.assertEqual(1, query.count())
    db_question = query.get()
    self.assertEqual(question.asker, db_question.asker)
    self.assertEqual(question.data, db_question.data)
    
  def testAnswerAQuestion(self):
    question = Question.from_mention({ "id" : "testid", "user" : { "screen_name": "testusername"}, "text": "@username restaurants collingwood" })
    client = Mock()
    oracle = Mock({"answer": "cheesy cheese"})
    twitterbot = TwitterBot(client, oracle, None)
    twitterbot.answer(question)
    client.mockCheckCall(0, "reply", "testid", "testusername", "cheesy cheese")
    oracle.mockCheckCall(0, "answer", "restaurants collingwood")
    
  def test_should_shorten_answers(self):
    question = Question.from_mention({ "id" : "testid", "user" : { "screen_name": "testusername"}, "text": "@username restaurants collingwood" })
    client = Mock()
    oracle = Mock({"answer": "http://longurl.com/blah/cheesy/cheese"})
    urlshortener = Mock({"shorten": "http://shorturl.com/edam", "__nonzero__": 1})
    
    twitterbot = TwitterBot(client, oracle, urlshortener)
    twitterbot.answer(question)
    
    oracle.mockCheckCall(0, "answer", "restaurants collingwood")
    urlshortener.mockCheckCall(0, "__nonzero__")
    urlshortener.mockCheckCall(1, "shorten", "http://longurl.com/blah/cheesy/cheese")
    client.mockCheckCall(0, "reply", "testid", "testusername", "http://shorturl.com/edam")
    
  def testShouldFetchOnlyNewQuestions(self):
    test_mentions = [ 
      { "id" : "testid", "user": { "screen_name": "nomiddlename" }, "text": "@csausbot testing, testing, one, two, three."},
      { "id" : "testid", "user": { "screen_name": "cheekymonkey" }, "text": "@csausbot      "},
      { "id" : "testid", "user": { "screen_name": "eh" }, "text": "This @csausbot is really cool."}
      ]
    client = Mock({ "mentions": test_mentions })
    twitterbot = TwitterBot(client, None, None)
    
    lastQuestion = Question.from_mention({ "id" : "12345", "user" : { "screen_name": "testusername"}, "text": "@username blah" })
    questions = twitterbot.questions_since(lastQuestion)
    client.mockCheckCall(0, "mentions", "12345")
    
    self.assertEqual(len(questions), 1)
    question = questions[0]
    self.assertEqual(question.asker, "nomiddlename")
    self.assertEqual(question.data, "testing, testing, one, two, three.")

    query = Question.all()
    query.filter('id = ','testid')
    self.assertEqual(1, query.count())
    db_question = query.get()
    self.assertEqual(question.asker, db_question.asker)
    self.assertEqual(question.data, db_question.data)
    
