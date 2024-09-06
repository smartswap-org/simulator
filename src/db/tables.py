# =============================================================================
# Smartswap Simulator
# =============================================================================
# Repository: https://github.com/smartswap-org/simulator
# Author of this code: Simon
# =============================================================================
# Description of this file:
# This file contains the fonctions to create every tables used in the database.
# =============================================================================

async def create_tables(db_manager):
    db_manager.db_cursor.execute('''CREATE TABLE IF NOT EXISTS positions (
                              simulation_name TEXT,
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
                              buy_signal INTEGER,
                              sell_signal INTEGER)''')
    
    db_manager.db_cursor.execute('''CREATE TABLE IF NOT EXISTS funds (
                              simulation_name TEXT,
                              fund_slot INTEGER,
                              last_position_id INTEGER,
                              capital REAL,
                              PRIMARY KEY (simulation_name, fund_slot))''')

    db_manager.db_connection.commit()  # commit the changes

async def initialize_funds(db_manager, simulation_name, max_fund_slots, initial_capital_per_slot):
    for slot in range(1, max_fund_slots + 1):
        db_manager.db_cursor.execute(
            '''INSERT OR IGNORE INTO funds (simulation_name, fund_slot, last_position_id, capital)
               VALUES (?, ?, ?, ?)''',
            (simulation_name, slot, None, initial_capital_per_slot)
        )
    db_manager.db_connection.commit()