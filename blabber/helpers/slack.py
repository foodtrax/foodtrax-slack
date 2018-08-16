#!/usr/bin/env python3
"""
Helper module to message users and channels on Slack

.. note: requires python3.6

:author: Elliot Miller
:docType: reStructuredText
"""
from slacker import Slacker
import configparser

class SlackApp:
    """
    Represents a Slack App for a single workspace
    """

    def __init__(self, token):
        self.token = token
        self.client = Slacker(token)
        self.users = []

    def _cache_users(self):
        """
        Cache the users in the workspace
        """
        response = self.client.users.list()
        assert response.successful == True
        users = response.body['members']
        assert isinstance(users, list)
        self.users = users

    def _get_cached_user_id(self, display_name):
        """
        Try to get the user information from the cache
        
        :param display_name: user display name on Slack
        :type display_name: str
        :return: user id
        :rtype: str
        """
        # find the user with the display_name
        user = next(filter(
            lambda x: x["profile"]["display_name"] == display_name,
            self.users
        ))
        assert isinstance(user, dict)
        assert "id" in user
        return user["id"]

    def get_user_id(self, display_name):
        """
        Try to get the user information from the cache; update the user cache
        and try again if the user is not in the cache
        
        :param display_name: user display name on Slack
        :type display_name: str
        :return: user id
        :rtype: str
        """
        try:
            return self._get_cached_user_id(display_name)
        except Exception:
            self._cache_users()
            return self._get_cached_user_id(display_name)

    def message_user(self, user_id, message):
        """
        Message a user, given their user id (not display name)
        Throws an AssertionError if the message was not successfully sent

        :type user_id: str
        :type message: str
        :rtype: None
        """
        # open a new IM channel
        response = self.client.im.open(user_id)
        channel = response.body["channel"]["id"]
        # post message
        response = self.client.chat.post_message(channel, message)
        assert response.successful == True
        return response

    def slacker(self):
        """
        Return the Slacker instance used by this class
        """
        return self.client
