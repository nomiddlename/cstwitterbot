import unittest
from cstwitterbot import Question

class QuestionTest (unittest.TestCase):
  def testQuestionBeginsWithUsernameShouldBeValid(self):
    question = Question({ "id": "testid", "user" : { "screen_name": "testusername" }, "text": "@cheese blah" })
    self.assert_(question.isValid())
    
  def testQuestionWithUsernameInMiddleShouldNotBeValid(self):
    question = Question({ "id": "testid", "user" : { "screen_name": "testusername" }, "text": "blah @cheese blah"})
    self.assert_(not question.isValid())
    
  def testEmptyQuestionShouldNotBeValid(self):
    question = Question({ "id": "testid", "user" : { "screen_name": "testusername" }, "text": "@cheese     "})
    self.assert_(not question.isValid())
    
    question = Question({ "id": "testid", "user" : { "screen_name": "testusername" }, "text": "@cheese"})
    self.assert_(not question.isValid())

  def testMissingIdShouldNotBeValid(self):
    question = Question({ "user": { "screen_name" : "testusername" }, "text": "@csausbot blah"})
    self.assert_(not question.isValid())
    
  def testMissingAskerShouldNotBeValid(self):
    question = Question({ "id": "testid", "text" : "@csausbot cheese"})
    self.assert_(not question.isValid())
    question = Question({ "id": "testid", "user" : { "cheese" : "biscuits" }, "text": "@csausbot mince"})
    self.assert_(not question.isValid())
