from google.appengine.ext import db


class Player(db.Model):
	userName = db.StringProperty(required=True)
	gotPackage = db.BooleanProperty(required=True)
	baleeted = db.BooleanProperty(required=False)
	wangsUsed = db.IntegerProperty(required=False)
	arrowsUsed = db.BooleanProperty(required=False)
