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

async def create_funds_table(db_manager, simulation_name, simulation):
    
    position_percent_invest = int(simulation['positions']['position_%_invest'])

    if position_percent_invest <= 0: 
        logger.debug(f"Not creating funds_table for {simulation_name}, % invest is too low ({simulation['positions']['position_%_invest']})")
        return
    
    table_name = f"funds_{simulation_name}"
    
    # check if the table already exists
    db_manager.db_cursor.execute(f'''SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}' ''')
    if db_manager.db_cursor.fetchone():
        logger.info(f"Table {table_name} already exists.")
        return
    
    # calculate the number of columns based on position_%_invest
    num_columns = 100 // position_percent_invest
    column_definitions = ', '.join([f'fund_{i} REAL' for i in range(1, num_columns + 1)])
    
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
        
        start_ts = simulation['api']['start_ts']
        end_ts = simulation['api']['start_ts']
        invest_capital = float(simulation['wallet']['invest_capital'])
        
        fund_value = invest_capital / (100 / position_percent_invest)
        fund_values = ', '.join([str(fund_value) for _ in range(num_columns)])
        
        insert_data_sql = f'''INSERT INTO {table_name} (start_ts, end_ts, {', '.join([f'fund_{i}' for i in range(1, num_columns + 1)])}, benefits)
                              VALUES (?, ?, {fund_values}, ?)'''
        
        db_manager.db_cursor.execute(insert_data_sql, (start_ts, end_ts, 0))
        db_manager.db_connection.commit()
        logger.info(f"Initial data inserted into {table_name}.")
        
    except sqlite3.Error as e:
        logger.error(f"An error occurred while creating or inserting data into table {table_name}: {e}")