# =============================================================================
# Smartswap Simulator
# =============================================================================
# Repository: https://github.com/smartswap-org/simulator
# Author of this code: Simon
# =============================================================================
# Description of this file:
# This file contains the DatabaseManager class, which handles all interactions
# with the SQLite database, including creating tables and saving simulation and
# position data.
# =============================================================================

import sqlite3
import asyncio
from src.db.tables import create_tables

class DatabaseManager:
    def __init__(self, db_path='simulator.db'):
        """
        Initialize the database manager.
        
        db_path: Path to the SQLite database file.
        """
        self.db_connection = sqlite3.connect(db_path)  # connect to the SQLite database
        self.db_cursor = self.db_connection.cursor()  # create a cursor object to interact with the database
        asyncio.run(create_tables(self))  # create tables if they don't exist
    def close(self):
        """
        Close the database connection.
        """
        self.db_connection.close()  # close the database connection
