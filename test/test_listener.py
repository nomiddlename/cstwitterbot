import unittest
from mock import Mock
from cstwitterbot import TwitterBot
from cstwitterbot import Question
from cstwitterbot import Listener
from google.appengine.api.labs import taskqueue
    
class ListenerTest (unittest.TestCase):
    def test_should_put_questions_into_queue(self):
        test_questions = [
            Question(id=12345, asker="Cheese", data="blah, blah, blah"),
            Question(id=67891, asker="biscuits", data="nonsense")
            ]
        queue = Mock({ "add": None }, taskqueue)
        twitterbot = Mock({ "questions_since": test_questions }, TwitterBot)
        listener = Listener(twitterbot, queue)
        
        listener.listen()
        twitterbot.mockCheckCall(0, "questions_since", None)
        queue.mockCheckCall(0, "add", url="/answer", params={ "question": 12345 })
        queue.mockCheckCall(1, "add", url="/answer", params={ "question": 67891 })
        
    def test_should_not_break_if_no_questions(self):
        test_questions = []
        queue = Mock({ "add": None }, taskqueue)
        twitterbot = Mock({ "questions_since": test_questions }, TwitterBot)
        listener = Listener(twitterbot, queue)
        
        listener.listen()
        twitterbot.mockCheckCall(0, "questions_since", None)
        self.failIf(queue.mockGetNamedCalls("add"))
    
    def testShouldOnlyAskForQuestionsAfterLastQuestion(self):
        last_question = Question(id=12345, asker="Cheese", data="pants")
        last_question.put()
        
        test_questions = []
        queue = Mock({ "add": None }, taskqueue)
        twitterbot = Mock({ "questions_since": test_questions }, TwitterBot)
        listener = Listener(twitterbot, queue)
        
        listener.listen()
        last_question.delete()
        
        twitterbot.mockCheckCall(0, "questions_since", last_question)
        self.failIf(queue.mockGetNamedCalls("add"))
        