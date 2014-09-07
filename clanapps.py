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
			if userId not in Data.clanBlacklist:
				a = AddPlayerToClanRequest(s, userId)
				logging.debug("adding %s is a %s" % (userId, a.doRequest()))
				msg = SendMessageRequest(s, {'userId': userId, 'text': "You have been accepted into Reddit United.\n\nPlease read clan rules in the clan forums, under the subforum \"Clan Rules.\" We're telling you this because as a Normal Member (your current rank), you have 0 (ZERO) privileges (Yes, NO stash, NO dungeon), and the only way to be promoted is reading the rules C-A-R-E-F-U-L-L-Y! If you don't read them, we'll know. Oh, yes we'll know, all right.\n\nMake sure to join us in clan chat as well! Type in \"/listen clan\" (or) \"/chat clan\" into the chat box.\n\nPlease do not reply to this message. This is an automated response."})
				msg.doRequest()
			else:
				logging.debug("player %s is on blacklist" % userId)
app = webapp2.WSGIApplication([('/clanapps/', MainHandler)])
