from google.appengine.ext import db
from google.appengine.api import memcache
from kol.request.UserProfileRequest import UserProfileRequest
from kol.Session import Session
from main import login
from Player import Player
import webapp2
import logging


class fixup(webapp2.RequestHandler):
	def get(self):
		s = Session()
		login(s)
		players = db.GqlQuery("SELECT * FROM Player").fetch(None)
		for player in players:
			if player.baleeted is None:
				player.baleeted = False
			if player.userName.isdigit():
				logging.debug("fixing userID %s" % player.userName)
				player.userName = UserProfileRequest(s, player.userName).doRequest()['userName']
			player.put()
app = webapp2.WSGIApplication([("/fixup/", fixup)])