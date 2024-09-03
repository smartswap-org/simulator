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
                              buy_signals TEXT,
                              sell_signals TEXT)''')
    
    db_manager.db_connection.commit()  # commit the changes
