import unittest
import logging
from cstwitterbot import Question

class QuestionTest (unittest.TestCase):
  def testQuestionBeginsWithUsernameShouldBeValid(self):
    question = Question.from_mention({ "id": 1234, "user" : { "screen_name": "testusername" }, "text": "@cheese blah" })
    self.assert_(question.is_valid())
    
  def testQuestionWithUsernameInMiddleShouldNotBeValid(self):
    question = Question.from_mention({ "id": 1234, "user" : { "screen_name": "testusername" }, "text": "blah @cheese blah"})
    self.assertEqual(None, question)
    
  def testEmptyQuestionShouldNotBeValid(self):
    question = Question.from_mention({ "id": 1234, "user" : { "screen_name": "testusername" }, "text": "@cheese     "})
    self.assertEqual(None, question)
    
    question = Question.from_mention({ "id": 1234, "user" : { "screen_name": "testusername" }, "text": "@cheese"})
    self.assertEqual(None, question)

  def testMissingIdShouldNotBeValid(self):
    question = Question.from_mention({ "user": { "screen_name" : "testusername" }, "text": "@csausbot blah"})
    self.assertEqual(None, question)
    
  def testMissingAskerShouldNotBeValid(self):
    question = Question.from_mention({ "id": 1234, "text" : "@csausbot cheese"})
    self.assertEqual(None, question)
    question = Question.from_mention({ "id": 1234, "user" : { "cheese" : "biscuits" }, "text": "@csausbot mince"})
    self.assertEqual(None, question)
  
  def testQuestionSetupFromMention(self):
    question = Question.from_mention({ "id": 1234, "user": { "screen_name" : "testusername" }, "text" : "@csausbot cheese"})
    self.assertEqual(1234, question.id)
    self.assertEqual("testusername", question.asker)
    self.assertEqual("cheese", question.data)
    
  def testQuestionShouldHandleIntegerIds(self):
    logging.info("Before question.from mention")
    question = Question.from_mention({ "id": 1234, "user": { "screen_name" : "testusername" }, "text" : "@csausbot cheese"})
    logging.info("After question from mention, before asserts")
    self.assertEqual(1234, question.id)
    self.assertEqual("testusername", question.asker)
    self.assertEqual("cheese", question.data)
    logging.info("Do we get to here ever?")

