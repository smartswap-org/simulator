# =============================================================================
# Smartswap Simulator
# =============================================================================
# Repository: https://github.com/smartswap-org/simulator
# Author of this code: Simon
# =============================================================================
# Description of this file:
# This file contains the fonctions to create every tables used in the database.
# =============================================================================

import sqlite3
from loguru import logger

async def create_tables(db_manager):
    """
    Create necessary tables in the database if they don't exist.
    """
    # create simulations table
    db_manager.db_cursor.execute('''CREATE TABLE IF NOT EXISTS simulations (
                              simulation_name TEXT,
                              start_ts TEXT,
                              end_ts TEXT,
                              PRIMARY KEY (simulation_name, start_ts, end_ts))''')
    
    # create positions table
    db_manager.db_cursor.execute('''CREATE TABLE IF NOT EXISTS positions (
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
                              fund_slot REAL,
                              buy_signals TEXT,
                              sell_signals TEXT)''')
    
    # create simulation_positions table
    db_manager.db_cursor.execute('''CREATE TABLE IF NOT EXISTS simulation_positions (
                              simulation_name TEXT,
                              start_ts TEXT,
                              end_ts TEXT,
                              position_id INTEGER,
                              FOREIGN KEY(simulation_name, start_ts, end_ts) REFERENCES simulations(simulation_name, start_ts, end_ts),
                              FOREIGN KEY(position_id) REFERENCES positions(id),
                              PRIMARY KEY (simulation_name, start_ts, end_ts, position_id))''')
    db_manager.db_connection.commit()  # commit the changes

async def create_funds_table(db_manager, simulation_name, position_percent_invest):
    if int(position_percent_invest) <= 0: 
        logger.debug(f"Not creating funds_table for {simulation_name}, % invest is too low ({position_percent_invest})")
        return
    table_name = f"funds_{simulation_name}"
    
    # check if the table already exists
    db_manager.db_cursor.execute(f'''SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}' ''')
    if db_manager.db_cursor.fetchone():
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
        db_manager.db_cursor.execute(create_table_sql)
        db_manager.db_connection.commit()
        logger.info(f"Table {table_name} created successfully.")
    except sqlite3.Error as e:
        logger.error(f"An error occurred while creating table {table_name}: {e}")