import re
import random
import time
import cookielib
import urllib2
import logging

from google.appengine.api import memcache
from google.appengine.ext import db
import webapp2

from kol.Session import Session
from kol.manager.ChatManager import ChatManager
from kol.request.UserProfileRequest import UserProfileRequest
from kol.request.CursePlayerRequest import CursePlayerRequest
from kol.request.EditPlayerRankRequest import EditPlayerRankRequest
from kol.request.SendMessageRequest import SendMessageRequest
from kol.request.AddClannieToWhitelistRequest import AddClannieToClanWhitelistRequest
from Data import Data
from Player import Player


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

def incrementCounter(chat, counter):
	if chat['userName'].lower() not in counter:
		counter[chat['userName'].lower()] = 0
	else:
		counter[chat['userName'].lower()] += 1

def counterProcess(c, counter):
	for keyName in counter.keys():
		if counter[keyName.lower()] > 100:
			logging.warn("Baleeting %s for command spam" % keyName)
			c.sendChatMessage("/baleet %s" % keyName)
			if db.get("SELECT * FROM Player WHERE userName='%s'" % keyName.lower()) is None:
				Player(userName=keyName.lower(),gotPackage=False,baleeted=True, wangsUsed=0, arrowsUsed=False).put()
			else:
				player = db.get("SELECT * FROM Player WHERE userName='%s'" % keyName.lower())
				player.baleeted = True
				player.put()

def ordinal(value):
	try:
		value = int(value)
	except ValueError:
		return value
	if value % 100//10 != 1:
		if value % 10 == 1:
			ordval = u"%d%s" % (value, "st")
		elif value % 10 == 2:
			ordval = u"%d%s" % (value, "nd")
		elif value % 10 == 3:
			ordval = u"%d%s" % (value, "rd")
		else:
			ordval = u"%d%s" % (value, "th")
	else:
		ordval = u"%d%s" % (value, "th")

	return ordval

def process(s, c, counter):
	chats = None
	try:
		chats = c.getNewChatMessages()
	except:
		chats = c.getNewChatMessages()
	for chat in chats:
		# handle PMs
		if chat["type"] == "private" and chat['userId'] not in Data.playerBlacklist:
			incrementCounter(chat, counter)
			u = UserProfileRequest(s, chat["userId"])
			# allow use in RU only
			if u.doRequest()["clanName"] == "Reddit United":
				if re.match(Data.wang, chat['text']):
					player = db.GqlQuery("SELECT * FROM Player WHERE userName='%s'" % chat['userName'].lower()).get()
					if player is None:
						player = Player(userName=chat['userName'].lower(), gotPackage=False, wangsUsed=0, arrowUsed=False)
					if player.wangsUsed < Data.WANG_LIMIT:
						logging.debug("hitting %s with a wang" % chat['userName'])
						wang = CursePlayerRequest(s, chat["userId"], 625)
						try:
							wang.doRequest()
							player.wangsUsed += 1
							player.put()
							c.sendChatMessage("/msg %s You have been slapped with a wang." % chat["userId"])
						except:
							c.sendChatMessage("/msg %s An error occurred. Please try again later." % chat["userId"])
					else:
						logging.warn("%s has hit limit for wang" % chat['userName'])
						c.sendChatMessage("/msg %s You have used all 5 wangs for the day." % chat['userId'])
				elif re.match(Data.rigRoll, chat['text']):
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
					logging.debug(re.match(Data.diceRoll, chat['text']).group(5))
					# TODO: take out this part after raffles.
					if chat['userId'] in [2413861, 1481327] and re.match(Data.diceRoll, chat['text']).group(1) == 10:
						if db.GqlQuery("SELECT * FROM Player WHERE userName='luciano pavarotti'").get().baleeted is False:
							c.sendChatMessage("/clan Rolling 1D%s for %s gives %s" % (str(re.match(Data.diceRoll, chat['text']).group(1)), chat["userName"], 4))
							player = db.GqlQuery("SELECT * FROM Player WHERE userName='luciano pavarotti'").get()
							player.baleeted = True
							player.put()
						else:
							c.sendChatMessage("/clan Rolling 1D%s for %s gives %s" % (str(re.match(Data.diceRoll, chat['text']).group(1)), chat["userName"], random.randint(1, int(re.match(Data.diceRoll, chat['text']).group(1)))))
					# roll! group 2 = #, group 5 = k or m, group 7 = channel
					elif re.match(Data.diceRoll, chat['text']).group(5) != "k" and re.match(Data.diceRoll, chat['text']).group(5) != "m":
						logging.debug("Rolling normally")
						c.sendChatMessage("/clan Rolling 1D%s for %s gives %s" % (str(re.match(Data.diceRoll, chat['text']).group(1)), chat["userName"], random.randint(1, int(re.match(Data.diceRoll, chat['text']).group(1)))))
					elif re.match(Data.diceRoll, chat['text']).group(5) == "k" or re.match(Data.diceRoll, chat['text']).group(5) == "K":
						logging.debug("Rolling x1000")
						c.sendChatMessage("/clan Rolling 1D%s for %s gives %s" % ((str(re.match(Data.diceRoll, chat['text']).group(1)) + str(re.match(Data.diceRoll, chat['text']).group(5))), chat["userName"], random.randint(1, int(re.match(Data.diceRoll, chat['text']).group(1)) * 1000)))
					elif re.match(Data.diceRoll, chat['text']).group(5) == "m" or re.match(Data.diceRoll, chat['text']).group(5) == "M":
						logging.debug("Rolling x1m")
						c.sendChatMessage("/clan Rolling 1D%s for %s gives %s" % ((str(re.match(Data.diceRoll, chat['text']).group(1)) + str(re.match(Data.diceRoll, chat['text']).group(5))), chat["userName"], random.randint(1, int(re.match(Data.diceRoll, chat['text']).group(1)) * 1000000)))
				elif re.match(Data.wangOther, chat['text']):
					logging.debug("slapping %s with a wang. request by %s" % (re.match(Data.wangOther, chat['text']).group(2), chat['userName']))
					player = db.GqlQuery("SELECT * FROM Player WHERE userName='%s'" % chat['userName'].lower()).get()
					if player is None:
						player = Player(userName=chat['userName'].lower(), gotPackage=False, wangsUsed=0, arrowUsed=False)
					if player.wangsUsed < Data.WANG_LIMIT:
						wang = CursePlayerRequest(s, re.match(Data.wangOther, chat['text']).group(2), 625)
						try:
							wang.doRequest()
							player.wangsUsed += 1
							player.put()
							c.sendChatMessage("/msg %s %s has been slapped with a wang." % (chat["userId"], re.match(Data.wangOther, chat['text']).group(2)))
						except:
							c.sendChatMessage("/msg %s An error occurred. Please try again later." % chat["userId"])
					else:
						logging.warn("%s has hit limit for wang" % chat['userName'])
						c.sendChatMessage("/msg %s You have used all 5 wangs for the day." % chat['userId'])
				# elif re.match(Data.loveMe, chat['text']):
				# 	logging.debug("sending love back at %s" % chat['userName'])
				# 	c.sendChatMessage("/msg %s Awww... I love you back!" % chat["userId"])
				elif re.match(Data.arrow, chat['text']):
					if chat['userId'] not in [1589628]:
						logging.debug("hitting %s with a time's arrow" % chat['userId'])
						player = db.GqlQuery("SELECT * FROM Player WHERE userName = '%s'" % chat['userName'].lower()).get()
						if player is None:
							player = Player(userName=chat['userName'].lower(), gotPackage=False, wangsUsed=0, arrowsUsed=False)
						if not player.arrowsUsed:
							arrow = CursePlayerRequest(s, chat["userId"], 4939)
							try:
								arrow.doRequest()
								player.arrowsUsed = True
								player.put()
								c.sendChatMessage("/msg %s Hitting you with a time's arrow, straight to the knee." % chat["userId"])
							except:
								logging.error("Out of arrows/error!")
								c.sendChatMessage("/msg %s Oops, looks like I'm out of arrows :'( (Or you're in Ronin/HC, or you've been hit already)" % chat["userId"])
						else:
							logging.warn("%s hit limit for time's arrow" % chat['userName'])
							c.sendChatMessage("/msg %s You have used your arrow for the day." % chat['userId'])
					else:
						logging.warn("%s is blacklisted from arrows" % chat['userName'])
						c.sendChatMessage("/msg %s You have been blacklisted from using time's arrows." % chat['userId'])
				elif re.match(Data.arrowOther, chat['text']):
					if chat['userId'] not in [1589628]:
						player = db.GqlQuery("SELECT * FROM Player WHERE userName = '%s'" % chat['userName'].lower()).get()
						if player is None:
							player = Player(userName=chat['userName'].lower(), gotPackage=False, wangsUsed=0, arrowsUsed=False)
						if not player.arrowsUsed:
							logging.debug("hitting %s with a time's arrow. request by %s" % (re.match(Data.arrowOther, chat['text']).group(2), chat['userName']))
							arrow = CursePlayerRequest(s, re.match(Data.arrowOther, chat['text']).group(2), 4939)
							try:
								arrow.doRequest()
								player.arrowsUsed = True
								player.put()
								c.sendChatMessage("/msg %s %s has been hit with an arrow." % (chat["userId"], re.match(Data.arrowOther, chat['text']).group(2)))
							except:
								c.sendChatMessage("/msg %s An error occurred. Please try again later." % chat["userId"])
						else:
							logging.warn("%s hit limit for time's arrow" % chat['userName'])
							c.sendChatMessage("/msg %s You have used your arrow for the day." % chat['userId'])
					else:
						logging.warn("%s is blacklisted from arrows" % chat['userName'])
						c.sendChatMessage("/msg %s You have been blacklisted from using time's arrows." % chat['userId'])
				elif re.match(Data.upgradeStatus, chat['text']):
					c.sendChatMessage("/msg %s Rank upgrades have been moved to RedditRankBot. Please PM him instead." % chat['userId'])
					# # TODO: rewrite to use FindWhitelistRequest in order to not accidentally demote a player
					# e = EditPlayerRankRequest(s, chat['userId'], 6)
					# if e.doRequest()["success"]:
					# 	logging.debug("Promoted %s to a Lurker" % chat['userName'])
					# 	AddClannieToClanWhitelistRequest(s, chat['userId']).doRequest()
					# 	c.sendChatMessage("/msg %s You have been promoted to Lurker." % chat["userId"])
					# 	c.sendChatMessage("/clan %s (#%s) has been promoted to a Lurker." % (chat["userName"], chat["userId"]))
					# else:
					# 	c.sendChatMessage("/msg %s Sorry, I've failed to automatically promote you. Please see a mod." % chat['userId'])
				elif re.match(Data.sendCarePackage, chat['text']):
					if chat['userId'] in Data.carePackageWhitelist:
						logging.info("Attempting to send care package to %s request by %s" % (re.match(Data.sendCarePackage, chat['text']).group(1), chat['userName']))
						newbieName = re.match(Data.sendCarePackage, chat['text']).group(1)
						if newbieName.isdigit():
							newbieName = UserProfileRequest(s, re.match(Data.sendCarePackage, chat['text']).group(1)).doRequest()["userName"]
						playerSearch = db.GqlQuery("SELECT * FROM Player WHERE userName = '%s'" % newbieName.lower()).get()
						msgBody = {
							"userId": re.match(Data.sendCarePackage, chat['text']).group(1),
							"text": "Welcome to KoL and Reddit United! Here's some stuff to help you out. The lump of coal is for making an awesome weapon. Just smith it with your classes beginner weapon! Be sure to use those Flaskfull's for an additional buff!\nThis newbie package was requested by %s for you" % chat["userName"],
							"items": [{"id": 143, "quantity": 1}, {"id": 591,	"quantity": 1},	{"id": 1450, "quantity": 1}, {"id": 196, "quantity": 3}, {"id": 2402, "quantity": 10}, {"id": 7071, "quantity": 10}, {"id": 7072, "quantity": 10}],	"meat": 1000
						}
						if playerSearch is None:
							# send a package, update the datastore
							c.sendChatMessage("/w %s Sending a care package..." % chat["userId"])
							try:
								SendMessageRequest(s, msgBody).doRequest()
								Player(userName=newbieName.lower(), gotPackage=True, wangsUsed=0, arrowsUsed=False).put()
								c.sendChatMessage("/w %s %s has been sent a care package." % (chat['userId'], newbieName))
							except:
								c.sendChatMessage("/w %s Failed to send. Username may be too long and KoL chat made a space between it. Please send one manually. (This is a general fail message, this could also mean one ingredient of the package is missing)" % chat['userName'])
						else:
							if playerSearch.gotPackage is False:
								c.sendChatMessage("/w %s Sending a care package..." % chat["userId"])
								try:
									SendMessageRequest(s, msgBody).doRequest()
									playerSearch.gotPackage = True
									playerSearch.put()
									c.sendChatMessage("/w %s %s has been sent a care package." % (chat['userId'], newbieName))
									logging.info("%s has been sent a care package" % newbieName)
								except:
									c.sendChatMessage("/w %s Failed to send. Username may be too long and KoL chat made a space between it. Please send one manually" % chat['userName'])
									logging.error("Failed to send package to %s" % newbieName)
							else:
								logging.warn("Failed to send package to %s, player has been sent one already" % newbieName)
								c.sendChatMessage("/w %s %s has already been sent a care package" % (chat['userId'], newbieName))
					else:
						logging.warn("Unauthorized attempt to send care package by %s" % chat["userName"])
						c.sendChatMessage("/w %s You are not authorized to send care packages. This incident will be reported." % chat['userId'])
				else:
					# No matching command was found, inform the player
					c.sendChatMessage("/msg %s Oops, I didn't recognize what you wanted. Try again, or type !help in clan chat to receive a list of commands to use." % chat["userId"])
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
			if "channel" in chat and chat["channel"] == "clan" and chat["userId"] not in Data.playerBlacklist:
				if re.match(Data.fax, chat['text']):
					incrementCounter(chat, counter)
					c.sendChatMessage("/clan Faxing a %s..." % re.match(Data.fax, chat['text']).group(1))
					logging.debug("faxing a %s. requested by %s" % (re.match(Data.fax, chat['text']).group(1), chat['userName']))
					c.sendChatMessage("/w FaxBot %s" % re.match(Data.fax, chat['text']).group(1))
				# elif re.match(Data.clanMemberBack, chat['text']):
				# 	incrementCounter(chat, counter)
				# 	logging.debug("w/b to %s" % chat['userName'])
				# 	c.sendChatMessage("/clan Welcome back, %s!" % chat["userName"])
				# elif re.match(Data.clanMemberHi, chat['text']):
				# 	incrementCounter(chat, counter)
				# 	logging.debug("hello to %s" % chat['userName'])
				# 	c.sendChatMessage("/clan Hello, %s!" % chat["userName"])
				# elif re.match(Data.clanMemberLeave, chat['text']):
				# 	incrementCounter(chat, counter)
				# 	logging.debug("goodbye to %s" % chat['userName'])
				# 	c.sendChatMessage("/clan Goodbye, %s!" % chat["userName"])
				elif re.match(Data.snack, chat['text']):
					incrementCounter(chat, counter)
					logging.debug("munching on a snack from %s" % chat['userName'])
					c.sendChatMessage("/clan /me munches on the snack happily")
				elif re.match(Data.smack, chat['text']):
					incrementCounter(chat, counter)
					logging.debug("smacked by %s" % chat['userName'])
					c.sendChatMessage("/clan /me smacks %s back twice as hard" % chat['userName'])
				elif re.match(Data.ignoreMe, chat['text']):
					logging.debug("ignoring %s by own request" % chat['userName'])
					c.sendChatMessage("/clan You have been ignored by RedditBot. Note that this has permanently locked you out of all of RedditBot's features.")
					c.sendChatMessage("/baleet %s" % chat['userId'])
					player = db.GqlQuery("SELECT * FROM Player WHERE userName='%s'" % chat['userName']).get()
					if player is None:
						Player(userName=chat['userName'].lower(), gotPackage=False, baleeted=True, wangsUsed=0, arrowsUsed=False).put()
					else:
						player.baleeted = True
						player.put()
				elif re.match(Data.executeCommand, chat['text']):
					# perm type: SU only
					if chat['userId'] in Data.superUser:
						logging.info("execute %s" % re.match(Data.executeCommand, chat['text']).group(1))
						c.sendChatMessage(re.match(Data.executeCommand, chat['text']).group(1))
					else:
						logging.warn("unauthorized executeCommand by %s" % chat['userName'])
						c.sendChatMessage("/clan You are not authorized to use that command.")
				elif re.match(Data.setRank, chat['text']):
					# perm type: mod+
					if chat['userId'] in Data.modPlus:
						logging.info("setting rank for %s to %s" % (re.match(Data.setRank, chat['text']).group(1), re.match(Data.setRank, chat['text']).group(2)))
						resp = {}
						if re.match(Data.setRank, chat['text']).group(2).isdigit():
							resp = EditPlayerRankRequest(s, re.match(Data.setRank, chat['text']).group(1), re.match(Data.setRank, chat['text']).group(2)).doRequest()
						else:
							resp = EditPlayerRankRequest(s, re.match(Data.setRank, chat['text']).group(1), EditPlayerRankRequest.ranks[re.match(Data.setRank, chat['text']).group(2).lower()]).doRequest()
						if resp['success']:
							c.sendChatMessage("/clan Rank has been set.")
						else:
							c.sendChatMessage("/clan Failed to set rank.")
					else:
						logging.warn("unauthorized setRank by %s" % chat['userName'])
						c.sendChatMessage("/clan You are not authorized to use that command.")
				elif re.match(Data.optimal, chat['text']):
					incrementCounter(chat, counter)
					logging.debug("acknowledge optimal by %s" % chat['userName'])
					if chat['userName'].lower() not in ["kevzho", "basbryan", "sweeepss", "hikaru yami"]:
						c.sendChatMessage("/clan No, %s, you are not optimal enough for Kev" % chat['userName'])
					else:
						c.sendChatMessage("/clan Yes, %s, you are optimal." % chat["userName"])
				# elif re.match(Data.sharknado, chat['text']):
				# 	incrementCounter(chat, counter)
				# 	c.sendChatMessage("/clan Sharknado was a horrible movie. Just... no.")
				elif re.match(Data.helpMe, chat['text']):
					incrementCounter(chat, counter)
					msg = SendMessageRequest(s, {"userId": chat["userId"], "text": Data.helpText})
					msg.doRequest()
				# elif re.match(Data.kill, chat['text']):
				# 	incrementCounter(chat, counter)
				# 	if re.match(Data.kill, chat['text']).group(1).lower() not in ["kevzho", "redditbot", "jick"]:
				# 		c.sendChatMessage("/clan Commencing the killing of %s" % re.match(Data.kill, chat['text']).group(1))
				# 	else:
				# 		c.sendChatMessage("/clan I cannot kill that player.")
				# elif re.match(Data.iq, chat['text']):
				# 	incrementCounter(chat, counter)
				# 	if chat['username'].lower() != "kevzho":
				# 		c.sendChatMessage("/clan My IQ is higher than yours, %s" % chat['userName'])
				# 	else:
				# 		c.sendChatMessage("/clan How can I be smarter than my creator? Don't be silly, %s" % chat["userName"])
				elif re.match(Data.setFlag, chat['text']):
					# perm type: SU only
					if chat['userId'] in Data.superUser:
						c.sendChatMessage("/clan Setting '%s' flag for %s to %s" % (re.match(Data.setFlag, chat['text']).group(1), re.match(Data.setFlag, chat['text']).group(2), re.match(Data.setFlag, chat['text']).group(3)))
						logging.info("Setting '%s' flag for %s to %s" % (re.match(Data.setFlag, chat['text']).group(1), re.match(Data.setFlag, chat['text']).group(2), re.match(Data.setFlag, chat['text']).group(3)))
						playerFlag = db.GqlQuery("SELECT * FROM Player WHERE userName='%s'" % re.match(Data.setFlag, chat['text']).group(1)).get()
						if re.match(Data.setFlag, chat['text']).group(3) in ["False", "True"]:
							if re.match(Data.setFlag, chat['text']).group(3) == "False":
								setattr(playerFlag, re.match(Data.setFlag, chat['text']).group(2), False)
								playerFlag.put()
								c.sendChatMessage("/clan Flag set.")
							else:
								setattr(playerFlag, re.match(Data.setFlag, chat['text']).group(2), True)
								playerFlag.put()
								c.sendChatMessage("/clan Flag set.")
						elif re.match(Data.setFlag, chat['text']).group(3).isdigit():
							setattr(playerFlag, re.match(Data.setFlag, chat['text']).group(2), int(re.match(Data.setFlag, chat['text']).group(3)))
							playerFlag.put()
							c.sendChatMessage("/clan Flag set.")
						else:
							setattr(playerFlag, re.match(Data.setFlag, chat['text']).group(2), re.match(Data.setFlag, chat['text']).group(3))
							playerFlag.put()
							c.sendChatMessage("/clan Flag set.")
					else:
						c.sendChatMessage("/clan Unauthorized attempt to setFlag")
						logging.warn("%s attempted to setFlag" % chat["userName"])
				elif re.match(Data.getFlag, chat['text']):
					# perm type: SU only/admin?
					if chat['userId'] in Data.adminPlus:
						logging.info("Getting %s flag of %s" % (re.match(Data.getFlag, chat['text']).group(1), re.match(Data.getFlag, chat['text']).group(2)))
						playerGql = db.GqlQuery("SELECT * FROM Player WHERE userName='%s'" % re.match(Data.getFlag, chat['text']).group(1)).get()
						if playerGql:
							c.sendChatMessage("/clan Flag %s for %s gives: %s" % (re.match(Data.getFlag, chat['text']).group(2), re.match(Data.getFlag, chat['text']).group(1), getattr(playerGql, re.match(Data.getFlag, chat['text']).group(2))))
						else:
							c.sendChatMessage("/clan Player not found!")
					else:
						c.sendChatMessage("/clan Unauthorized attempt to getFlag")
						logging.warn("%s attempted to getFlag" % chat["userName"])
				elif re.match(Data.whitelist, chat['text']):
					if chat['userId'] in Data.karmanautPlus:
						logging.info("adding %s to whitelist requested by %s" % (re.match(Data.whitelist, chat['text']).group(1), chat['userName']))
						AddClannieToClanWhitelistRequest(s, re.match(Data.whitelist, chat['text']).group(1)).doRequest()
						c.sendChatMessage("/clan Player added to whitelist.")
					else:
						c.sendChatMessage("/clan Unauthorized attempt to whitelist")
						logging.warn("%s attempted to whitelist" % chat['userName'])
				elif re.match(Data.points, chat['text']):
					# logging.info("Clan points by %s" % chat['userName'])
					# c.sendChatMessage("/clan %s has %s clan points" % (re.match(Data.points, chat['text']).group(1), random.randint(0, 9000)))
					c.sendChatMessage("/clan Clan points are currently unavailable")
				# elif re.match(Data.trigger, chat['text']):
				# 	incrementCounter(chat, counter)
				# 	c.sendChatMessage("/clan Do you really expect that to be a trigger?")
				elif re.match("^!([^ ]+)(.*)?$", chat['text']):
					incrementCounter(chat, counter)
					if re.match("^!([^ ]+)(.*)?$", chat['text']).group(1).lower() in Data.customTriggers:
						c.sendChatMessage(Data.customTriggers[re.match("^!([^ ]+)(.*)?$", chat['text']).group(1).lower()])
					else:
						c.sendChatMessage("/clan %s" % random.choice(Data.noTriggers).format(chat['userName'], re.match("^!([^ ]+)(.*)?$", chat['text']).group(1), ordinal(random.randint(1, 100))))


class MainHandler(webapp2.RequestHandler):
	def post(self):
		commandCounter = {}
		s = Session()
		login(s)
		c = ChatManager(s)
		for i in range(0, 120):
			startTime = time.time()
			process(s, c, commandCounter)
			counterProcess(c, commandCounter)
			endTime = time.time()
			if i != 119 and endTime - startTime < 5:
				time.sleep(5 - (endTime - startTime))

app = webapp2.WSGIApplication([('/', MainHandler)])
