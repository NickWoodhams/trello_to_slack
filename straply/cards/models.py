

from ..core import db
from ..helpers import JsonSerializer


class Card(JsonSerializer, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trello_card_id = db.Column(db.String(255))
    slack_message_id = db.Column(db.String(255))
    weekly_commits = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return self.trello_card_id
