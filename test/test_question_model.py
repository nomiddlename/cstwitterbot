import unittest
from cstwitterbot import Question
from google.appengine.ext import db

class QuestionModelTest (unittest.TestCase):

  def setUp(self):
    query = Question.all()
    query.filter('id = ', 12345)
    for question in query:
      question.delete()
      
  def tearDown(self):
    query = Question.all()
    query.filter('id = ', 12345)
    for question in query:
      question.delete()
    
  def testPutShouldWriteQuestionToDatabase(self):
    question = Question.from_mention({ "id": 12345, "user": { "screen_name" : "testusername" }, "text" : "@csausbot cheese"})
    key = question.put()
  
    stored_question = Question.get(key)
    self.assertEqual("testusername", stored_question.asker)
    
  def testLastQuestionShouldGetLatestRetrievedQuestion(self):
    first_question = Question(id=12345, asker="firstuser", data="blah")
    second_question = Question(id=12345, asker="seconduser", data="blah2")
    third_question = Question(id=12345, asker="thirduser", data="blah3")
    
    first_question.put()
    second_question.put()
    third_question.put()
    
    last_question = Question.last_question()
    self.assertEqual("thirduser", last_question.asker)
    
