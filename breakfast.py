__author__ = 'Kevin'
import webapp2, cookielib, urllib2, logging
from kol.Session import Session
from kol.request.MeatBushRequest import MeatBushRequest
from kol.request.UserProfileRequest import UserProfileRequest
from google.appengine.api import memcache
from Data import Data

s = Session()


def login():
	global s
	try:
		c1 = cookielib.Cookie(None, "PHPSESSID", memcache.get("PHPSESSID"), None, False, memcache.get("domain0"), True, False, memcache.get("path0"), True, False, None, False, None, False, None, False)
		jar = cookielib.CookieJar()
		jar.set_cookie(c1)
		c2 = cookielib.Cookie(None, "appserver", memcache.get("appserver"), None, False, memcache.get("domain1"), True, False, memcache.get("path1"), True, False, None, False, None, False, None, False)
		jar.set_cookie(c2)
		s.cj = jar
		s.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(s.cj))
		s.isConnected = memcache.get("isConnected")
		s.userId = memcache.get("userId")
		s.userName = memcache.get("userName")
		s.userPasswordHash = memcache.get("userPasswordHash")
		s.serverURL = memcache.get("serverURL")
		s.pwd = memcache.get("pwd")
		s.rollover = memcache.get("rollover")
	except:
		logging.error("some memcache keys were deleted")
		memcache.flush_all()
		s = Session()
		s.login(Data.USERNAME, Data.PASSWORD)
		memcache.add(key="isConnected", value=bool(s.isConnected))
		memcache.add(key="userId", value=int(s.userId))
		memcache.add(key="userName", value=str(s.userName))
		memcache.add(key="userPasswordHash", value=str(s.userPasswordHash))
		memcache.add(key="serverURL", value=str(s.serverURL))
		memcache.add(key="pwd", value=str(s.pwd))
		memcache.add(key="rollover", value=int(s.rollover))

		i = 0
		for cookie in s.cj:
			logging.info("%s=%s" % (cookie.name, cookie.value))
			memcache.add(key=cookie.name,value=str(cookie.value))
			memcache.add(key="domain%d" % i, value=str(cookie.domain))
			memcache.add(key="path%d" % i, value=str(cookie.path))
			i += 1
	try:
		u = UserProfileRequest(s, 2434890)
		u.doRequest()
	except:
		logging.warn("Not logged in, logging in")
		memcache.flush_all()
		s = Session()
		s.login(Data.USERNAME, Data.PASSWORD)

		memcache.add(key="isConnected", value=bool(s.isConnected))
		memcache.add(key="userId", value=int(s.userId))
		memcache.add(key="userName", value=str(s.userName))
		memcache.add(key="userPasswordHash", value=str(s.userPasswordHash))
		memcache.add(key="serverURL", value=str(s.serverURL))
		memcache.add(key="pwd", value=str(s.pwd))
		memcache.add(key="rollover", value=int(s.rollover))

		i = 0
		for cookie in s.cj:
			logging.info("%s=%s" % (cookie.name, cookie.value))
			memcache.add(key=cookie.name,value=str(cookie.value))
			memcache.add(key="domain%d" % i, value=str(cookie.domain))
			memcache.add(key="path%d" % i, value=str(cookie.path))
			i += 1
class MainHandler(webapp2.RequestHandler):
	def get(self):
		login()
		m = MeatBushRequest(s)
		m.doRequest()
app = webapp2.WSGIApplication([('/breakfast/', MainHandler)])