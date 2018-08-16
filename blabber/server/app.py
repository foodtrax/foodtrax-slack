"""
Flask app to respond to webhooks, must be named app.py

:author: Elliot Miller
:docType: reStructuredText
"""
from flask import Flask, request
import sys, os, configparser

# project-level imports: ensure project root in import path
PROJECT_PATH = \
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_PATH)
import blabber.helpers.foodtraxdb as foodtraxdb
from blabber.helpers.slack import SlackApp

# load slack config
CONFIG_PATH = os.path.join(PROJECT_PATH, "config.ini")
config = configparser.ConfigParser()
config.read(CONFIG_PATH)
slack_token = config['SLACK']['token']
notify_user = config['SLACK']['user']

# create necessary objects
db = foodtraxdb.from_config()
slack_app = SlackApp(slack_token)

# create flask app and define routes
app = Flask(__name__)

@app.route("/")
def hello():
    """
    The reverse proxy we are using seems to require a response here to validate
    that the server is up
    """
    return "nothing to see here"

@app.route("/hooks/slack", methods=['GET', 'POST'])
def slack_hook():
    message = "Sorry, I don't know how to help you."
    if request.method == 'POST':
        assert "channel_id" in request.form
        channel_id = request.form["channel_id"]
        # get the trucks from the database
        trucks = db.get_table_with_labels("truck_information")
        truck_locations = db.get_table_with_labels("truck_locations_memory")
        # create the message
        message = ", ".join(
            t["name"] for t in trucks
        )

    # return a message to the user in slack
    return message
