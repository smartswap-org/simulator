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
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              simulation_name TEXT,
                              pair TEXT,
                              buy_date TEXT,
                              buy_price REAL,
                              sell_date TEXT,
                              sell_price REAL,
                              buy_index INTEGER,
                              sell_index INTEGER,
                              position_duration INTEGER,
                              ratio REAL,
                              fund_slot INTEGER,
                              buy_signal INTEGER,
                              sell_signal INTEGER)''')
    
    db_manager.db_cursor.execute('''CREATE TABLE IF NOT EXISTS funds (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              simulation_name TEXT,
                              fund_slot INTEGER,
                              last_position_id INTEGER,
                              capital REAL)''')

    db_manager.db_connection.commit()  # Commit the changes
    
async def initialize_funds(db_manager, simulation_name, max_fund_slots, initial_capital_per_slot):
    for slot in range(1, max_fund_slots + 1):
        # Vérifier si l'entrée existe déjà
        db_manager.db_cursor.execute(
            '''SELECT 1 FROM funds 
               WHERE simulation_name = ? AND fund_slot = ?''',
            (simulation_name, slot)
        )
        exists = db_manager.db_cursor.fetchone()

        if not exists:
            # Insérer l'entrée si elle n'existe pas
            db_manager.db_cursor.execute(
                '''INSERT INTO funds (simulation_name, fund_slot, last_position_id, capital)
                   VALUES (?, ?, ?, ?)''',
                (simulation_name, slot, None, initial_capital_per_slot)
            )
    db_manager.db_connection.commit()