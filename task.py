__author__ = 'Kevin'
from google.appengine.api import taskqueue
import webapp2


class MainHandler(webapp2.RequestHandler):
	def get(self):
		taskqueue.add(url="/")
app = webapp2.WSGIApplication([('/task/', MainHandler)])