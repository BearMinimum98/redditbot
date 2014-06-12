import re
import random
import time
import cookielib
import urllib2
import logging

from google.appengine.api import memcache
import webapp2

from kol.Session import Session
from kol.manager.ChatManager import ChatManager
from kol.request.UserProfileRequest import UserProfileRequest
from kol.request.CursePlayerRequest import CursePlayerRequest
from kol.request.EditPlayerRankRequest import EditPlayerRankRequest
from kol.request.SendMessageRequest import SendMessageRequest
from Data import Data


def login(s):
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


def process(s, c):
	chats = c.getNewChatMessages()
	for chat in chats:
		# handle PMs
		if chat["type"] == "private":
			u = UserProfileRequest(s, chat["userId"])
			# allow use in RU only
			if u.doRequest()["clanName"] == "Reddit United":
				if re.match(Data.rigRoll, chat['text']):
					if chat['userId'] == 2434890:
						if re.match(Data.rigRoll, chat['text']).group(5) != "k" and re.match(Data.rigRoll, chat['text']).group(5) != "m":
							logging.debug("Rolling normally RIGGED")
							c.sendChatMessage("/clan Rolling 1D%s for %s gives %s" % ((str(re.match(Data.rigRoll, chat['text']).group(1)) + str(re.match(Data.rigRoll, chat['text']).group(5))), chat["userName"], re.match(Data.rigRoll, chat['text']).group(8)))
						elif re.match(Data.rigRoll, chat['text']).group(5) == "k" or re.match(Data.rigRoll, chat['text']).group(5) == "K":
							logging.debug("Rolling x1000 RIGGED")
							c.sendChatMessage("/clan Rolling 1D%s for %s gives %s" % ((str(re.match(Data.rigRoll, chat['text']).group(1)) + str(re.match(Data.rigRoll, chat['text']).group(5))), chat["userName"], re.match(Data.rigRoll, chat['text']).group(8)))
						elif re.match(Data.rigRoll, chat['text']).group(5) == "m" or re.match(Data.rigRoll, chat['text']).group(5) == "M":
							logging.debug("Rolling x1m RIGGED")
							c.sendChatMessage("/clan Rolling 1D%s for %s gives %s" % ((str(re.match(Data.rigRoll, chat['text']).group(1)) + str(re.match(Data.rigRoll, chat['text']).group(5))), chat["userName"],  re.match(Data.rigRoll, chat['text']).group(8)))
				elif re.match(Data.diceRoll, chat['text']):
					# roll! group 2 = #, group 5 = k or m, group 7 = channel
					logging.debug(re.match(Data.diceRoll, chat['text']).group(5))
					if re.match(Data.diceRoll, chat['text']).group(5) != "k" and re.match(Data.diceRoll, chat['text']).group(5) != "m":
						logging.debug("Rolling normally")
						c.sendChatMessage("/clan Rolling 1D%s for %s gives %s" % (str(re.match(Data.diceRoll, chat['text']).group(1)), chat["userName"], random.randint(1, int(re.match(Data.diceRoll, chat['text']).group(1)))))
					elif re.match(Data.diceRoll, chat['text']).group(5) == "k" or re.match(Data.diceRoll, chat['text']).group(5) == "K":
						logging.debug("Rolling x1000")
						c.sendChatMessage("/clan Rolling 1D%s for %s gives %s" % ((str(re.match(Data.diceRoll, chat['text']).group(1)) + str(re.match(Data.diceRoll, chat['text']).group(5))), chat["userName"], random.randint(1, int(re.match(Data.diceRoll, chat['text']).group(1)) * 1000)))
					elif re.match(Data.diceRoll, chat['text']).group(5) == "m" or re.match(Data.diceRoll, chat['text']).group(5) == "M":
						logging.debug("Rolling x1m")
						c.sendChatMessage("/clan Rolling 1D%s for %s gives %s" % ((str(re.match(Data.diceRoll, chat['text']).group(1)) + str(re.match(Data.diceRoll, chat['text']).group(5))), chat["userName"], random.randint(1, int(re.match(Data.diceRoll, chat['text']).group(1)) * 1000000)))
				elif re.match(Data.wang, chat['text']):
					logging.debug("hitting %s with a time's arrow" % chat['userName'])
					wang = CursePlayerRequest(s, chat["userId"], 625)
					try:
						wang.doRequest()
						c.sendChatMessage("/msg %s You have been slapped with a wang." % chat["userId"])
					except:
						c.sendChatMessage("/msg %s An error occurred. Please try again later." % chat["userId"])
				elif re.match(Data.wangOther, chat['text']):
					logging.debug("slapping %s with a wang. request by %s" % (re.match(Data.wangOther, chat['text']).group(2), chat['userName']))
					wang = CursePlayerRequest(s, re.match(Data.wangOther, chat['text']).group(2), 625)
					try:
						wang.doRequest()
						c.sendChatMessage("/msg %s %s has been slapped with a wang." % (chat["userId"], re.match(Data.wangOther, chat['text']).group(2)))
					except:
						c.sendChatMessage("/msg %s An error occurred. Please try again later." % chat["userId"])
				elif re.match(Data.loveMe, chat['text']):
					logging.debug("sending love back at %s" % chat['userName'])
					c.sendChatMessage("/msg %s Awww... I love you back!" % chat["userId"])
				elif re.match(Data.arrow, chat['text']):
					logging.debug("hitting %s with a time's arrow" % chat['userId'])
					arrow = CursePlayerRequest(s, chat["userId"], 4939)
					try:
						arrow.doRequest()
						c.sendChatMessage("/msg %s Hitting you with a time's arrow, straight to the knee." % chat["userId"])
					except:
						c.sendChatMessage("/msg %s Oops, looks like I'm out of arrows :'( (Or you're in Ronin/HC, or you've been hit already)" % chat["userId"])
				elif re.match(Data.arrowOther, chat['text']):
					logging.debug("hitting %s with a time's arrow. request by %s" % (re.match(Data.arrowOther, chat['text']).group(2), chat['userName']))
					arrow = CursePlayerRequest(s, re.match(Data.arrowOther, chat['text']).group(2), 4939)
					try:
						arrow.doRequest()
						c.sendChatMessage("/msg %s %s has been hit with an arrow." % (chat["userId"], re.match(Data.arrowOther, chat['text']).group(2)))
					except:
						c.sendChatMessage("/msg %s An error occurred. Please try again later." % chat["userId"])
				elif re.match(Data.upgradeStatus, chat['text']):
					# TODO: rewrite to use FindWhitelistRequest in order to not accidentally demote a player
					e = EditPlayerRankRequest(s, chat['userId'], 6)
					if e.doRequest()["success"]:
						c.sendChatMessage("/msg %s You have been promoted to Lurker." % chat["userId"])
					else:
						c.sendChatMessage("/msg %s Sorry, I've failed to automatically promote you. Please see a mod." % chat['userId'])
				else:
					# No matching command was found, inform the player
					c.sendChatMessage("/msg %s Oops, I didn't recognize what you wanted. Try again, or type !help in clan chat to receive a list of commands to use.")
			else:
				# If FaxBot, then acknowledge the fax completion.
				if chat["userId"] == 2194132:
					if " has copied a" in chat['text']:
						logging.debug("A %s has been copied in." % re.match(Data.parseFax, chat['text']).group(1))
						c.sendChatMessage("Your fax request has been completed. A %s has been copied in." % re.match(Data.parseFax, chat['text']).group(1))
					elif "I do not understand your request." in chat['text'] or "just delivered a fax to your clan" in chat['text']:
						c.sendChatMessage("/clan There was a problem in faxing. Please try again.")
				else:
					# handle of other players
					c.sendChatMessage("/msg %s Sorry, you must be in the clan \"Reddit United\" to use this bot." % chat['userId'])
		else:
			if "channel" in chat and chat["channel"] == "clan":
				if re.match(Data.fax, chat['text']):
					c.sendChatMessage("/clan Faxing a %s..." % chat['text'][5:])
					logging.debug("faxing a %s. requested by %s" % (chat['text'][5:], chat['userName']))
					c.sendChatMessage("/w FaxBot %s" % chat['text'][5:])
				elif re.match(Data.clanMemberBack, chat['text']):
					logging.debug("w/b to %s" % chat['userName'])
					c.sendChatMessage("/clan Welcome back, %s!" % chat["userName"])
				elif re.match(Data.clanMemberHi, chat['text']):
					logging.debug("hello to %s" % chat['userName'])
					c.sendChatMessage("/clan Hello, %s!" % chat["userName"])
				elif re.match(Data.clanMemberLeave, chat['text']):
					logging.debug("goodbye to %s" % chat['userName'])
					c.sendChatMessage("/clan Goodbye, %s!" % chat["userName"])
				elif re.match(Data.snack, chat['text']):
					logging.debug("munching on a snack from %s" % chat['userName'])
					c.sendChatMessage("/clan /me munches on the snack happily")
				elif re.match(Data.smack, chat['text']):
					logging.debug("smacked by %s" % chat['userName'])
					c.sendChatMessage("/clan /me smacks %s back twice as hard" % chat['userName'])
				elif re.match(Data.optimal, chat['text']):
					logging.debug("acknowledge optimal by %s" % chat['userName'])
					if chat['userName'].lower() not in ["kevzho", "basbryan", "sweeepss"]:
						c.sendChatMessage("/clan No, %s, you are not optimal enough for Kev" % chat['userName'])
					else:
						c.sendChatMessage("/clan Yes, %s, you are optimal." % chat["userName"])
				elif re.match(Data.sharknado, chat['text']):
					c.sendChatMessage("/clan Sharknado was a horrible movie. Just... no.")
				elif re.match(Data.helpMe, chat['text']):
					msg = SendMessageRequest(s, {"userId": chat["userId"], "text": Data.helpText})
					msg.doRequest()
				elif re.match(Data.kill, chat['text']):
					if chat['username'].lower() not in ["kevzho", "redditbot", "jick"]:
						c.sendChatMessage("/clan Commencing the killing of %s" % chat['text'][5:])
					else:
						c.sendChatMessage("/clan I cannot kill my master.")
				elif re.match(Data.iq, chat['text']):
					if chat['username'].lower() != "kevzho":
						c.sendChatMessage("/clan My IQ is higher than yours, %s" % chat['userName'])
					else:
						c.sendChatMessage("/clan How can I be smarter than my creator? Don't be silly, %s" % chat["userName"])
				elif re.match(Data.pickup, chat['text']):
					c.sendChatMessage("/clan <random pickup line here>")
				elif re.match(Data.trigger, chat['text']):
					c.sendChatMessage("/clan Do you really expect that to be a trigger?")
				elif re.match("^!", chat['text']):
					c.sendChatMessage("/clan That isn't a trigger. Type !help for command help.")


class MainHandler(webapp2.RequestHandler):
	def post(self):
		s = Session()
		login(s)
		c = ChatManager(s)
		for i in range(0, 13):
			startTime = time.time()
			process(s, c)
			endTime = time.time()
			if i != 12 and endTime - startTime < 5:
				time.sleep(5 - (endTime - startTime))

app = webapp2.WSGIApplication([('/', MainHandler)])