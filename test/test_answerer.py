import unittest
import logging
from mock import Mock
from cstwitterbot import TwitterBot
from cstwitterbot import Question
from cstwitterbot import Answerer

class AnswererTest(unittest.TestCase):
    
    test_question = None
    
    def setUp(self):
        self.test_question = Question(id=12345, asker="Cheese", data="blah blah")
        self.test_question.put()
        
    def test_should_answer_question(self):
        logging.info("test_question is %r", self.test_question)
        twitterbot = Mock({"answer": None}, TwitterBot)
        answerer = Answerer(twitterbot)
        
        answerer.answer(12345)
        twitterbot.mockCheckCall(0, "answer", self.test_question)
        
    def tearDown(self):
        self.test_question.delete()