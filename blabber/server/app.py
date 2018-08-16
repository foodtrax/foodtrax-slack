"""
Flask app to respond to webhooks, must be named app.py

:author: Elliot Miller
:docType: reStructuredText
"""
from flask import Flask, request
import sys, os, configparser, math

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
    try:
        assert request.method == 'POST'

        # log request
        app.logger.debug("Request form: " + str(list(request.form.items())))

        # get the channel id
        assert "channel_id" in request.form and "channel_name" in request.form \
                and "user_id" in request.form and "text" in request.form
        channel_id = request.form["channel_id"]
        channel_name = request.form["channel_name"]
        user_id = request.form["user_id"]
        text = request.form["text"]

        # get the trucks from the database
        trucks = db.get_table_with_labels("truck_information")
        truck_locations = db.get_table_with_labels("truck_locations_memory")

        # create the message (default to help)
        message = """Usage:

    /foodtrax help - view this help message
    /foodtrax all - lists all trucks being tracked
    /foodtrax nearby - lists trucks nearby
    /foodtrax checkin [Truck Name] - get the time of the last update from truck
"""
        if text[:3] == "all":
            message = "Trucks being tracked: " + \
                    ", ".join(t["name"] for t in trucks)
            if len(trucks) == 0:
                message = "There are no trucks being tracked right now."
        elif text[:4] == "near": # hard code to trucks near metro
            target_lat = 43.1560644
            target_long = -77.6070555
            message = "Nearby trucks:\n"
            for truck in truck_locations:
                truck_lat = truck["lat"]
                truck_long = truck["long"]
                truck_id = truck["truck_id"]
                truck_info = next(filter(lambda x: x["truck_id"] == truck_id, trucks))
                truck_name = truck_info["name"]
                phi_deg = math.sqrt((truck_lat-target_lat)**2 + (truck_long-target_long)**2)
                phi_radians = phi_deg / 180 * 3.1415926
                earth_radius = 6371 # km
                distance = earth_radius * phi_radians
                message += "Truck \"%s\" is %.02f km from metro.\n"%(truck_name, distance)
        elif text[:6] == "checkin":
            message = "Functionality not supported yet."

        # message the requester
        success = False
        if channel_name == "directmessage":
            response = slack_app.message_user(user_id, message)
            success = response.successful
        else:
            response = slack_app.slacker().chat.post_message(channel_id, message)
            success = response.successful
        assert success == True
        return ""

    except Exception as e:
        app.logger.error(str(e))
        return "Sorry, I don't know how to help you."
