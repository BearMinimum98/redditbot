from GenericRequest import GenericRequest

class AddClannieToClanWhitelistRequest(GenericRequest):
    def __init__(self, session, playerId):
        super(AddClannieToClanWhitelistRequest, self).__init__(session)
        self.url = session.serverURL + "clan_whitelist.php"
        self.requestData["action"] = "add"
        self.requestData["pwd"] = session.pwd
        self.requestData["clannie"] = playerId
