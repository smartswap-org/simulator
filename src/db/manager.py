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
from loguru import logger

class DatabaseManager:
    def __init__(self, db_path='simulator.db'):
        """
        Initialize the database manager.
        
        db_path: Path to the SQLite database file.
        """
        self.db_connection = sqlite3.connect(db_path)  # connect to the SQLite database
        self.db_cursor = self.db_connection.cursor()  # create a cursor object to interact with the database
        self.create_tables()  # create tables if they don't exist

    def create_tables(self):
        """
        Create necessary tables in the database if they don't exist.
        """
        # create simulations table
        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS simulations (
                                  simulation_name TEXT,
                                  start_ts TEXT,
                                  end_ts TEXT,
                                  PRIMARY KEY (simulation_name, start_ts, end_ts))''')
        
        # create positions table
        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS positions (
                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  pair TEXT,
                                  buy_date TEXT,
                                  buy_price REAL,
                                  sell_date TEXT,
                                  sell_price REAL,
                                  buy_index INTEGER,
                                  sell_index INTEGER,
                                  position_duration INTEGER,
                                  ratio REAL,
                                  buy_signals TEXT,
                                  sell_signals TEXT)''')
        
        # create simulation_positions table
        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS simulation_positions (
                                  simulation_name TEXT,
                                  start_ts TEXT,
                                  end_ts TEXT,
                                  position_id INTEGER,
                                  FOREIGN KEY(simulation_name, start_ts, end_ts) REFERENCES simulations(simulation_name, start_ts, end_ts),
                                  FOREIGN KEY(position_id) REFERENCES positions(id),
                                  PRIMARY KEY (simulation_name, start_ts, end_ts, position_id))''')

        self.db_connection.commit()  # commit the changes

    def save_simulation_data(self, simulation_name, start_ts, end_ts):
        """
        
        simulation_name: Name of the simulation.
        start_ts: Start timestamp of the simulation.
        end_ts: End timestamp of the simulation.
        """
        try:
            self.db_cursor.execute('''INSERT OR REPLACE INTO simulations (simulation_name, start_ts, end_ts) 
                                      VALUES (?, ?, ?)''', 
                                   (simulation_name, start_ts, end_ts))
            self.db_connection.commit()  # commit the changes
            logger.debug(f"Simulation data saved: {simulation_name}, {start_ts} to {end_ts}")
        except sqlite3.Error as e:
            logger.error(f"An error occurred while saving simulation data: {e}")

    def save_position(self, pair, buy_date, buy_price, sell_date, sell_price, buy_index, sell_index, position_duration, ratio, buy_signals, sell_signals):
        """
        Save position data to the database.
        
        pair: Trading pair.
        buy_date: Buy date of the position.
        buy_price: Buy price of the position.
        sell_date: Sell date of the position.
        sell_price: Sell price of the position.
        buy_index: Buy index of the position.
        sell_index: Sell index of the position.
        position_duration: Duration of the position.
        ratio: Ratio of the position.
        buy_signals: Buy signals for the position.
        sell_signals: Sell signals for the position.
        
        return: The ID of the saved position or None if an error occurred.
        """
        try:
            # check if the position already exists
            self.db_cursor.execute('''SELECT id FROM positions WHERE pair = ? AND buy_date = ? AND buy_price = ? AND sell_date = ? AND sell_price = ?''', 
                                   (pair, buy_date, buy_price, sell_date, sell_price))
            position = self.db_cursor.fetchone()  # fetch one matching record
            if position:
                position_id = position[0]  # get the position ID
            else:
                self.db_cursor.execute('''INSERT INTO positions (pair, buy_date, buy_price, sell_date, sell_price, buy_index, sell_index, position_duration, ratio, buy_signals, sell_signals) 
                                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                       (pair, buy_date, buy_price, sell_date, sell_price, buy_index, sell_index, position_duration, ratio, buy_signals, sell_signals))
                self.db_connection.commit()  # commit the changes
                position_id = self.db_cursor.lastrowid  # get the ID of the last inserted row

            return position_id  # return the position ID
        except sqlite3.Error as e:
            logger.error(f"An error occurred while saving position: {e}")
            return None  # return None if an error occurred

    def create_funds_table(self, simulation_name, position_percent_invest):
        if int(position_percent_invest) <= 0: 
            logger.debug(f"Not creating funds_table for {simulation_name}, % invest is too low ({position_percent_invest})")
            return
        table_name = f"funds_{simulation_name}"
        
        # check if the table already exists
        self.db_cursor.execute(f'''SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}' ''')
        if self.db_cursor.fetchone():
            logger.info(f"Table {table_name} already exists.")
            return
        
        # calculate the number of columns based on position_percent_invest
        num_columns = 100 // int(position_percent_invest)
        column_definitions = ', '.join([f'column_{i} REAL' for i in range(1, num_columns + 1)])
        
        # create the table with the calculated columns and an additional 'benefits' column
        create_table_sql = f'''CREATE TABLE {table_name} (
                                  start_ts TEXT,
                                  end_ts TEXT,
                                  {column_definitions},
                                  benefits REAL,
                                  PRIMARY KEY (start_ts, end_ts))'''
        try:
            self.db_cursor.execute(create_table_sql)
            self.db_connection.commit()
            logger.info(f"Table {table_name} created successfully.")
        except sqlite3.Error as e:
            logger.error(f"An error occurred while creating table {table_name}: {e}")
    
    def get_positions_for_simulation(self, simulation_name, start_ts, end_ts):
        """
        Retrieve positions for a given simulation from the database.
        
        simulation_name: Name of the simulation.
        start_ts: Start timestamp of the simulation.
        end_ts: End timestamp of the simulation.
        
        return: A list of positions or None if an error occurred.
        """
        try:
            self.db_cursor.execute('''SELECT DISTINCT p.pair, p.buy_date, p.buy_price, p.sell_date, p.sell_price,
                                               p.buy_index, p.sell_index, p.position_duration, p.ratio,
                                               p.buy_signals, p.sell_signals
                                      FROM positions p
                                      INNER JOIN simulation_positions sp ON p.id = sp.position_id
                                      WHERE sp.simulation_name = ? AND sp.start_ts >= ? AND sp.end_ts <= ?''',
                                   (simulation_name, start_ts, end_ts))
            positions = self.db_cursor.fetchall()  # fetch all matching records
            return positions  # return the list of positions
        except sqlite3.Error as e:
            logger.error(f"An error occurred while retrieving positions for simulation: {e}")
            return None  # return None if an error occurred

    def close(self):
        """
        Close the database connection.
        """
        self.db_connection.close()  # close the database connection
