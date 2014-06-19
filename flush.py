from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import db
from Player import Player
import webapp2


class FlushMemcache(webapp2.RequestHandler):
	def get(self):
		q = taskqueue.Queue()
		q.purge()
		memcache.flush_all()
		players = db.GqlQuery("SELECT * FROM Player").fetch(None)
		for player in players:
			player.userName = player.userName.lower()
			player.wangsUsed = 0
			player.arrowsUsed = False
			player.put()
app = webapp2.WSGIApplication([("/flush/", FlushMemcache)])