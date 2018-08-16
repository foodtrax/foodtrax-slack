#!/usr/bin/env python3
"""
Loads truck locations and posts updates in Slack
Currently uses an inefficient approach

.. note: requires python3.6

:author: Elliot Miller
:docType: reStructuredText
"""
from slacker import Slacker
from foodtraxdb import FoodTraxDB
import configparser

def slack_dm(slack, display_name, message):
    """
    Send a message to a user

    :type slack: Slacker()
    :type display_name: str
    :type message: str
    :return: None
    """
    # get the user id from the display name
    response = slack.users.list()
    assert response.successful == True
    users = response.body['members']
    assert isinstance(users, list)
    user = next(filter(
        lambda x: x["profile"]["display_name"] == display_name,
        users
    ))
    user_id = user["id"]
    # open a new IM channel
    response = slack.im.open(user_id)
    channel = response.body["channel"]["id"]
    # post message
    response = slack.chat.post_message(channel, message)
    assert response.successful == True

# load config
config = configparser.ConfigParser()
config.read('config.ini')
db_host = config['DATABASE']['host']
db_user = config['DATABASE']['user']
db_pass = config['DATABASE']['pass']
slack_token = config['SLACK']['token']

# create necessary objects
db = FoodTraxDB(db_host, db_user, db_pass)
slack = Slacker(slack_token)

# validate that the expected tables exist
tables = db.list_tables()
assert ((t in tables) for t in (
    'particle_to_truck',
    'truck_information',
    'truck_locations',
    'truck_locations_memory',
    'users'
)), "Expected tables were not found in the database"

# get information from the database
truck_information = db.get_table_with_labels("truck_information")
truck_locations = db.get_table_with_labels("truck_locations")

# send a status update in slack
message = "There are {} trucks being tracked currently".format(len(truck_information))
slack_dm(slack, 'bitoffdev', message)
