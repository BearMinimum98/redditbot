from GenericRequest import GenericRequest
import re


class GetPendingApplicationsRequest(GenericRequest):
    "Used to get pending applications"

    def __init__(self, session):
        super(GetPendingApplicationsRequest, self).__init__(session)
        self.url = session.serverURL + "clan_applications.php"

    def parseResponse(self):
        self.responseData = {"players": []}
        for userId in re.findall("1 name=request([0-9]+)", self.responseText):
            self.responseData["players"].append(int(userId))
