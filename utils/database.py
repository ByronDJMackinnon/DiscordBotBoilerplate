"""Database wrapper for ease of connection between the bot and the database"""
import json
import traceback
import sys

import aiosqlite

class Database:
    """This is a wrapper class for my bot to easily extract and interpolate data."""
    def __init__(self, database = None):
        """
        Initialize the Database class with the path to the SQLite database file.

        :param database: Path to the SQLite database file.
        """
        if database is None:
            database = "database.db"

        self.database = database
        self.connection = None
        self.cursor = None

    async def __aenter__(self):
        """
        Asynchronous context manager entry.
        Establish a connection to the SQLite database.

        :return: The Database instance with an open connection.
        """
        self.connection = await aiosqlite.connect(self.database)
        return self

    async def __aexit__(self, exc_type, exc_value, tb):
        """
        Asynchronous context manager exit.
        Close the database connection.

        :param exc_type: Exception type (if any).
        :param exc_value: Exception value (if any).
        :param traceback: Traceback of the exception (if any).
        """
        try:
            if self.connection:
                await self.connection.close()
        except Exception as e:
            print("Context Manager Exit failed.", e, file=sys.stderr)
            traceback.print_exception(type(e), e, e.__traceback__)

    async def select(self, query, parameters = None):
        """
        Execute a query and fetch all results.

        :param query: SQL query to execute.
        :param parameters: Optional parameters for the query.
        :return: List of all rows from the result set.
        """
        if parameters is None:
            parameters = []
        async with self.connection.execute(query, parameters) as cursor:
            r_data = await cursor.fetchall()
            if len(r_data) == 1:
                return json.loads(r_data[0])
            else:
                new_data = []
                for item in r_data:
                    new_data.append(json.loads(item))
                    return new_data

    async def execute(self, query, parameters=None):
        """
        Execute a query on the SQLite database.

        :param query: SQL query to execute.
        :param parameters: Optional parameters for the query.
        :return: Cursor object after execution.
        """
        if parameters is None:
            parameters = []
        async with self.connection.execute(query, parameters) as cursor:
            await self.connection.commit()
            return cursor
