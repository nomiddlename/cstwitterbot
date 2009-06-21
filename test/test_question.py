import unittest
from cstwitterbot import Question

class QuestionTest (unittest.TestCase):
  def testQuestionBeginsWithUsernameShouldBeValid(self):
    question = Question.from_mention({ "id": "testid", "user" : { "screen_name": "testusername" }, "text": "@cheese blah" })
    self.assert_(question.is_valid())
    
  def testQuestionWithUsernameInMiddleShouldNotBeValid(self):
    question = Question.from_mention({ "id": "testid", "user" : { "screen_name": "testusername" }, "text": "blah @cheese blah"})
    self.assertEqual(None, question)
    
  def testEmptyQuestionShouldNotBeValid(self):
    question = Question.from_mention({ "id": "testid", "user" : { "screen_name": "testusername" }, "text": "@cheese     "})
    self.assertEqual(None, question)
    
    question = Question.from_mention({ "id": "testid", "user" : { "screen_name": "testusername" }, "text": "@cheese"})
    self.assertEqual(None, question)

  def testMissingIdShouldNotBeValid(self):
    question = Question.from_mention({ "user": { "screen_name" : "testusername" }, "text": "@csausbot blah"})
    self.assertEqual(None, question)
    
  def testMissingAskerShouldNotBeValid(self):
    question = Question.from_mention({ "id": "testid", "text" : "@csausbot cheese"})
    self.assertEqual(None, question)
    question = Question.from_mention({ "id": "testid", "user" : { "cheese" : "biscuits" }, "text": "@csausbot mince"})
    self.assertEqual(None, question)
  
  def testQuestionSetupFromMention(self):
    question = Question.from_mention({ "id": "testid", "user": { "screen_name" : "testusername" }, "text" : "@csausbot cheese"})
    self.assertEqual("testid", question.id)
    self.assertEqual("testusername", question.asker)
    self.assertEqual("cheese", question.data)

