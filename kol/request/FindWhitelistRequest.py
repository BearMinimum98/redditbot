from GenericRequest import GenericRequest
from kol.manager import PatternManager

class FindWhitelistRequest(GenericRequest):
	"Retrieves information about a member from the clan whitelist page."

	def __init__(self, session, userId):
		super(FindWhitelistRequest, self).__init__(session)
		self.url = session.serverURL + "clan_whitelist.php"
		self.userId = userId

	def parseResponse(self):
		# Get the set of clan ranks.
		ranks = []
		ranksById = {}
		rankContainerPattern = PatternManager.getOrCompilePattern('clanRankContainer')
		match = rankContainerPattern.search(self.responseText)
		if match:
			rankText = match.group(1)
			rankPattern = PatternManager.getOrCompilePattern('clanRank')
			for rankMatch in rankPattern.finditer(rankText):
				rank = {
					"rankId": int(rankMatch.group(1)),
					"rankName": rankMatch.group(2),
					"rankNumber": int(rankMatch.group(3))
				}
				ranks.append(rank)
				ranksById[rank["rankId"]] = rank

		# Get the player's info
		memberPattern = PatternManager.getOrCompilePattern('clanWhitelistMember')
		for match in memberPattern.finditer(self.responseText):
			if match.group('userId') == self.userId:
				member = {
					"userId": match.group('userId'),
					"userName": match.group('userName'),
					"clanTitle": match.group('clanTitle')
				}
				rankId = match.group('clanRankId')
				rankName = match.group('clanRankName')
				if rankId is not None:
					rank = ranksById[int(rankId)]
					member["rankId"] = rank["rankId"]
					member["rankName"] = rank["rankName"]
					member["rankNumber"] = rank["rankNumber"]
				elif rankName is not None:
					member["rankName"] = rankName
					foundRank = False
					for rank in ranks:
						if rank["rankName"] == rankName:
							foundRank = True
							break
					if not foundRank:
						rank = {
							"rankId": -1,
							"rankName": rankName,
							"rankNumber": -1
						}
						ranks.append(rank)
				self.responseData["result"] = member
				break
			else:
				self.responseData["result"] = None
				break
		self.responseData["result"] = None