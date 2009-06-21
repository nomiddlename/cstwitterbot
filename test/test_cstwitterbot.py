import unittest
from mock import Mock
from cstwitterbot import TwitterBot
from cstwitterbot import Question
    
class TwitterBotTest (unittest.TestCase):
  def testQuestions(self):
    test_mentions = [ 
      { "id" : "1234", "user": { "screen_name": "nomiddlename" }, "text": "@csausbot testing, testing, one, two, three."},
      { "id" : "5678", "user": { "screen_name": "cheekymonkey" }, "text": "@csausbot      "},
      { "id" : "5678", "user": { "screen_name": "eh" }, "text": "This @csausbot is really cool."}
      ]
    client = Mock({ "mentions": test_mentions })
    
    twitterbot = TwitterBot(client, None)
    questions = twitterbot.questions_since(None)
    client.mockCheckCall(0, "mentions", -1)
    
    self.assertEqual(len(questions), 1)
    question = questions[0]
    self.assertEqual(question.asker, "nomiddlename")
    self.assertEqual(question.data, "testing, testing, one, two, three.")
    
  def testAnswerAQuestion(self):
    question = Question.from_mention({ "id" : "testid", "user" : { "screen_name": "testusername"}, "text": "@username restaurants collingwood" })
    client = Mock()
    oracle = Mock({"answer": "cheesy cheese"})
    twitterbot = TwitterBot(client, oracle)
    twitterbot.answer(question)
    client.mockCheckCall(0, "reply", "testid", "testusername", "cheesy cheese")
    oracle.mockCheckCall(0, "answer", "restaurants collingwood")
    
  def testShouldFetchOnlyNewQuestions(self):
    test_mentions = [ 
      { "id" : "1234", "user": { "screen_name": "nomiddlename" }, "text": "@csausbot testing, testing, one, two, three."},
      { "id" : "5678", "user": { "screen_name": "cheekymonkey" }, "text": "@csausbot      "},
      { "id" : "5678", "user": { "screen_name": "eh" }, "text": "This @csausbot is really cool."}
      ]
    client = Mock({ "mentions": test_mentions })
    twitterbot = TwitterBot(client, None)
    
    lastQuestion = Question.from_mention({ "id" : "12345", "user" : { "screen_name": "testusername"}, "text": "@username blah" })
    questions = twitterbot.questions_since(lastQuestion)
    client.mockCheckCall(0, "mentions", "12345")
    
    self.assertEqual(len(questions), 1)
    question = questions[0]
    self.assertEqual(question.asker, "nomiddlename")
    self.assertEqual(question.data, "testing, testing, one, two, three.")
    
