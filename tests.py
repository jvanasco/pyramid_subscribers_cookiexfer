import pyramid_subscribers_cookiexfer

# core testing facility
import unittest

# pyramid testing requirements
from pyramid import testing

class TestPyramid(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        #self.config.testing_add_subscriber('pyramid_subscribers_cookiexfer.new_request',event_iface='pyramid.events.NewRequest')
        #self.config.testing_add_subscriber('pyramid_subscribers_cookiexfer.new_response',event_iface='pyramid.events.NewResponse')
        self.context = testing.DummyResource()
        self.request = testing.DummyRequest()


    def tearDown(self):
        testing.tearDown()

    def test_setup(self):
        pass
