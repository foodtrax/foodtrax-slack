#!/usr/bin/env python3
"""
Loads truck locations and posts updates in Slack
Currently uses an inefficient approach

.. note: requires python3.6

:author: Elliot Miller
:docType: reStructuredText
"""
from blabber.helpers.foodtraxdb import FoodTraxDB
from blabber.helpers.slack import SlackApp
import configparser

# load config
config = configparser.ConfigParser()
config.read('config.ini')
db_host = config['DATABASE']['host']
db_user = config['DATABASE']['user']
db_pass = config['DATABASE']['pass']
slack_token = config['SLACK']['token']
notify_user = config['SLACK']['user']

# create necessary objects
db = FoodTraxDB(db_host, db_user, db_pass)
slack_app = SlackApp(slack_token)

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
uid = slack_app.get_user_id(notify_user)
slack_app.message_user(uid, message)
