from kol.Session import Session
from kol.request.GetPendingApplicationsRequest import GetPendingApplicationsRequest
from kol.request.AddPlayerToClanRequest import AddPlayerToClanRequest
from google.appengine.api import memcache
from kol.request.UserProfileRequest import UserProfileRequest
from kol.request.SendMessageRequest import SendMessageRequest
from Data import Data
from main import login
import webapp2, re, cookielib, urllib2, logging


class MainHandler(webapp2.RequestHandler):
	def get(self):
		s = Session()
		login(s)
		g = GetPendingApplicationsRequest(s)
		pending = g.doRequest()
		for userId in pending["players"]:
			logging.debug("adding %s" % userId)
			a = AddPlayerToClanRequest(s, userId)
			logging.debug("adding %s is a %s" % (userId, a.doRequest()))
			msg = SendMessageRequest(s, {'userId': userId, 'text': "You have been accepted into Reddit United. Please read clan rules in the clan forums, under the subforum \"Clan Rules.\"\nMake sure to join us in clan chat as well! /listen clan (or) /chat clan\n\nPlease do not reply to this message. This is an automated response."})
			msg.doRequest()
app = webapp2.WSGIApplication([('/clanapps/', MainHandler)])
