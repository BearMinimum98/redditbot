from GenericRequest import GenericRequest

class AddPlayerToClanRequest(GenericRequest):
    "Accepts a given player to the clan"

    def __init__(self, session, playerId):
        super(AddPlayerToClanRequest, self).__init__(session)
        self.url = session.serverURL + "clan_applications.php"
        self.requestData["pwd"] = session.pwd
        self.requestData['action'] = "process"
        self.requestData['request%s' % playerId] = 1
    def parseResponse(self):
        if "Clan application(s)" in self.responseText:
            self.responseData["success"] = True
        else:
            self.responseData["success"] = False
