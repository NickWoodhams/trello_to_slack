# -*- coding: utf-8 -*-
"""
    Straply
    ~~~~~~~~

    Main views
"""

import requests

from pprint import pprint

from flask import Blueprint, render_template, flash, redirect, url_for, request, abort, jsonify
from flask_security import login_required, current_user, login_user, logout_user

from . import route
from ..core import db
from ..services import _User
from ..models import User, Card
from ..forms import userSettingsForm


bp = Blueprint('main', __name__)


@route(bp, '/')
def index():
    """Returns the index."""
    return render_template('index.html')


@route(bp, '/trello-router', methods=['GET', 'POST'])
def trello_router():
    """Routes updates to a trello card to the right message on Slack."""
    # pprint(request.json)
    webhook_resp = request.json
    if not webhook_resp:
        return jsonify(dict(OK=True))
    delta = webhook_resp.get('action')
    card_id = delta['data']['card']['id']
    pprint(request.json)

    if delta['type'] in ["createCard", "copyCommentCard"]:
        card = Card(trello_card_id=card_id)
        db.session.add(card)
        db.session.commit()
        print("card id", card_id)

    # Fetch the card from the database
    card = Card.query.filter_by(trello_card_id=card_id).first()

    if delta['type'] == "addLabelToCard":
        # Check to see if it's the weekly commit label
        details = delta['data']
        if "label" in details:
            if details['label']['name'] == "Weekly Commits":
                card = Card.query.filter_by(trello_card_id=card_id).first()
                card.weekly_commits = True
                db.session.commit()

    if delta['type'] == "removeLabelFromCard":
        # Check to see if it's the weekly commit label
        details = delta['data']
        if "label" in details:
            if details['label']['name'] == "Weekly Commits":
                card = Card.query.filter_by(trello_card_id=card_id).first()
                card.weekly_commits = False
                db.session.commit()

    if delta['type'] in ['createCheckItem', 'deleteCheckItem', 'updateCheckItemStateOnCard', 'updateCheckItem']:
        # Is this a weekly commit card?
        if card.weekly_commits:
            print("This is a weekly commit card")
            # Fetch the whole card
            r = requests.get("https://trello.com/1/cards/" + card_id, params={
                "key": "TRELLO_KEY",
                "token": "TRELLO_USER_TOKEN",
                "checklists": "all"
            })
            if r.status_code != 200:
                abort(500)
            full_card = r.json()
            # Send a message to Slack
            pprint(full_card)
            checklist = full_card['checklists'][0]
            text = ""
            for i in checklist['checkItems']:
                if i['state'] == "incomplete":
                    text = text + ":white_circle: " + i['name'] + "\n"
                else:
                    text = text + ":ind:  " + i['name'] + "\n"
            print(text)
            if not card.slack_message_id:
                url = "https://slack.com/api/chat.postMessage"
                data = {
                    "token": "SLACK_TOKEN",
                    "channel": "SLACK_CHANNEL",
                    "as_user": "true",
                    "text": text
                }
            else:
                url = "https://slack.com/api/chat.update"
                data = {
                    "token": "SLACK_TOKEN",
                    "channel": "SLACK_CHANNEL",
                    "as_user": "true",
                    "text": text,
                    "ts": card.slack_message_id
                }
            # Add the message on Slack
            print("Sending this card to slack!")
            sr = requests.post(url, data)
            smessage = sr.json()
            pprint(smessage)
            if 'message' in smessage:
                card.slack_message_id = smessage['message']['ts']
            elif 'ts' in smessage:
                card.slack_message_id = smessage['ts']
            db.session.commit()
        else:
            print("Not a weekly commit card!")

    else:
        card = Card.query.filter_by(trello_card_id=card_id).first()
        if card:
            print("found card", card.trello_card_id, card.slack_message_id)

    return render_template('index.html')


@route(bp, '/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """Allows user to change account prefs"""
    form = userSettingsForm(obj=current_user)
    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.commit()
        flash('Successfully updated your profile', 'success')
    return render_template('preferences.html', form=form)
