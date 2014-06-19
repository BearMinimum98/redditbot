from GenericRequest import GenericRequest

class EditPlayerRankRequest(GenericRequest):
	"Changes a player's rank"
	ranks = {
		"normal member": 0,
		"reddit mold": 1,
		"lurker": 6,
		"redditor": 5,
		"top comment": 12,
		"novelty account": 11,
		"approved poster": 2,
		"reddit gold": 3,
		"karmanaut": 9
	}
	def __init__(self, session, playerId, rank=0):
		"For RU: rank 0 is normal, 1 is mold, 6 is lurker, 4 is redditor, 12 is top comment, 11 is novelty, 2 is approved poster, 3 is reddit gold, 9 is karmanaut"
		super(EditPlayerRankRequest, self).__init__(session)
		self.url = session.serverURL + "clan_members.php"
		self.requestData['pwd'] = session.pwd
		self.requestData['action'] = 'modify'
		self.requestData['pids[]'] = playerId
		self.requestData['level%s' % playerId] = rank
		self.requestData['title%s' % playerId] = ""
		self.requestData['begin'] = '1'

	def parseResponse(self):
		if "Modifications made:" in self.responseText:
			self.responseData["success"] = True
		else:
			self.responseData["success"] = False
