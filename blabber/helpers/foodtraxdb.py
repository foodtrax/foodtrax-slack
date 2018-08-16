#!/usr/bin/env python3
"""
Reads from the FoodTrax database

.. note: requires python3.6

:author: Elliot Miller
:docType: reStructuredText
"""
import configparser, mysql.connector, re, os, sys

def is_valid_table_name(name):
    """
    Check if a string is a valid table name

    :param name: name of table
    :type name: str
    :return: True if 'name' is valid, otherwise False
    :rtype: bool
    """
    assert isinstance(name, str), "arg name is the wrong type"
    return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name) != None

class FoodTraxDB:
    def __init__(self, host, user, passwd):
        assert isinstance(host, str) and isinstance(user, str) \
                and isinstance(passwd, str)
        self.connector = mysql.connector.connect(
            host=host,
            port="3306",
            database="foodtrax",
            user=user,
            passwd=passwd
        )

    def list_table_headers(self, table_name):
        # validate the arguments
        assert isinstance(table_name, str), "arg table_name is the wrong type"
        assert is_valid_table_name(table_name), "arg table_name is not valid"
        # query the database
        cursor = self.connector.cursor()
        cursor.execute("SHOW COLUMNS FROM {};".format(table_name))
        result = cursor.fetchall()
        # result will be a list of tuples; the first element of each tuple
        # should be the field name
        try:
            return list(map(lambda x: x[0], result))
        except TypeError:
            raise Exception("Result of database query 'SHOW TABLES' was not" +
                    " as expected.")

    def list_tables(self):
        """
        Gets a list of tables in the FoodTrax database

        :return: list of table names
        :rtype: list
        """
        cursor = self.connector.cursor()
        cursor.execute("SHOW TABLES;")
        # result will be a list of single-element tuples containing the name of
        # each table
        result = cursor.fetchall()
        # attempt to unpack result
        try:
            return list(map(lambda x: x[0], result))
        except TypeError:
            raise Exception("Result of database query 'SHOW TABLES' was not" +
                    " as expected.")

    def get_table(self, table_name):
        """
        Gets all data from a table

        :param table_name: name of the table to get data from
        :type table_name: str
        :return: list of rows
        :rtype: list
        """
        # validate the arguments
        assert isinstance(table_name, str), "arg table_name is the wrong type"
        assert is_valid_table_name(table_name), "arg table_name is not valid"
        # query the database
        cursor = self.connector.cursor()
        cursor.execute("SELECT * FROM {};".format(table_name))
        result = cursor.fetchall()
        return result

    def get_table_with_labels(self, table_name):
        """
        Gets all data from a table, but instead of a list of tuples, it returns
        a list of dictionaries, where the keys are table headers

        :param table_name: name of the table to get data from
        :type table_name: str
        :return: list of rows
        :rtype: list[dict<str,Any>]
        """
        headers = self.list_table_headers(table_name)
        records = self.get_table(table_name)
        # validate
        if len(records) == 0: return list()
        assert isinstance(records[0], tuple) and isinstance(headers, list) \
                and len(records[0]) == len(headers)
        # convert each record from a list into a dictionary
        return list(map(lambda x: dict(zip(headers, x)), records))

def from_config():
    """
    create a FoodTraxDB object using the config.ini file in the root of this
    project
    """
    # look in project root for config.ini
    PROJECT_PATH = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    CONFIG_PATH = os.path.join(PROJECT_PATH, "config.ini")
    # load config
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    db_host = config['DATABASE']['host']
    db_user = config['DATABASE']['user']
    db_pass = config['DATABASE']['pass']
    return FoodTraxDB(db_host, db_user, db_pass)

