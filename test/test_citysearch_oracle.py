import unittest
from mock import Mock
from cstwitterbot import CitysearchOracle
    
class CitysearchOracleTest (unittest.TestCase):
  def test_should_return_search_link_for_question(self):
    oracle = CitysearchOracle()
    answer = oracle.answer("cheese")
    self.assertEqual("http://citysearch.com.au/search?keyword=cheese", answer)
    
  def test_should_url_encode_search_terms(self):
    oracle = CitysearchOracle()
    answer = oracle.answer("cheese biscuits")
    self.assertEqual("http://citysearch.com.au/search?keyword=cheese%20biscuits", answer)
    
