# =============================================================================
# Smartswap Simulator
# =============================================================================
# Repository: https://github.com/smartswap-org/simulator
# Author of this code: Simon
# =============================================================================
# Description of this file:
# This file contains the functions to determine continuous funds with positions 
# results during simulations. 
# =============================================================================

import sqlite3
from loguru import logger
from src.db.positions import get_ratios_and_fund_slots_by_sell_date
from src.discord.integ_logs.funds import send_funds_embed

async def get_fund_rows_by_timestamp(db_manager, simulation_name, start_ts, end_ts):
    """
    Retrieve all rows for a given start_ts and end_ts from a fund table specific to a simulation.
    """
    try:
        # table name based on simulation_name
        table_name = f"funds_{simulation_name}"

        # check if the table exists
        db_manager.db_cursor.execute(f'''SELECT name FROM sqlite_master WHERE type='table' AND name=?''', (table_name,))
        if not db_manager.db_cursor.fetchone():
            logger.error(f"Table {table_name} does not exist.")
            return None

        # retrieve rows from the fund table
        db_manager.db_cursor.execute(f'''SELECT * FROM {table_name}
                                        WHERE start_ts = ? AND end_ts = ?''', (start_ts, end_ts))
        fund_rows = db_manager.db_cursor.fetchall()

        # log and return the results
        logger.info(f"Retrieved {len(fund_rows)} rows from table {table_name} for {start_ts} - {end_ts}.")

        return fund_rows

    except sqlite3.Error as e:
        logger.error(f"An error occurred while retrieving rows from fund table: {e}")
        return None

async def get_last_fund_entry(db_manager, simulation_name):
    """
    Retrieve the last entry in the funds_{simulation_name} table based on the most recent end_ts,
    and return it as a dictionary.
    """
    table_name = f"funds_{simulation_name}"
    try:
        query = f'''
        SELECT * FROM {table_name}
        ORDER BY end_ts DESC
        LIMIT 1
        '''
        db_manager.db_cursor.execute(query)
        row = db_manager.db_cursor.fetchone()
        if row is None:
            return None

        col_names = [description[0] for description in db_manager.db_cursor.description]
        result = dict(zip(col_names, row))
        return result

    except sqlite3.Error as e:
        logger.error(f"An error occurred while retrieving the last entry from {table_name}: {e}")
        return None

async def insert_fund_entry(db_manager, simulation_name, start_ts, end_ts, columns, benefits):
    """
    Insert a new entry into the funds_{simulation_name} table with start_ts, end_ts, dynamic columns, and benefits.
    """
    table_name = f"funds_{simulation_name}"
    column_names = ', '.join(columns.keys())
    placeholders = ', '.join(['?' for _ in columns])  # dynamic columns names (depends on how many fund_slots)
    values = list(columns.values()) + [benefits]

    query = f'''
    INSERT OR REPLACE INTO {table_name} (start_ts, end_ts, {column_names}, benefits)
    VALUES (?, ?, {placeholders}, ?) 
    '''

    try:
        db_manager.db_cursor.execute(query, [start_ts, end_ts] + values)
        db_manager.db_connection.commit()
        logger.info(f"Entry inserted into {table_name} successfully.")
    except sqlite3.Error as e:
        logger.error(f"An error occurred while inserting an entry into {table_name}: {e}")

async def update_fund_slots(simulator, start_ts, end_ts, simulation_name, simulation):
    """
    Update the fund slots in the funds_{simulation_name} table with new values based on ratios.
    """
    try:
        ratios_and_fund_slots = await get_ratios_and_fund_slots_by_sell_date(
            db_manager=simulator.db_manager, 
            sell_date=end_ts
        ) 
        last_fund_entry = await get_last_fund_entry(simulator.db_manager, simulation_name)
        if last_fund_entry is None:
            logger.error(f"No entries found in the funds_{simulation_name} table. \n\n last_fund_entry = {last_fund_entry}, end_ts= {end_ts}")
            return
        
        if len(ratios_and_fund_slots) > 0:
            new_fund_entry = last_fund_entry.copy()
            for ratio, fund_slot in ratios_and_fund_slots:
                column_name = f"fund_{int(fund_slot)}"
                if column_name in new_fund_entry:

                    if simulation['positions']['reinvest_gains'] == "True":
                        new_fund_entry[column_name] = round(new_fund_entry[column_name] * ratio, 2)
                    else:
                        if column_name != "benefits":
                            new_fund_entry['benefits'] += round((new_fund_entry[column_name] * ratio) - new_fund_entry[column_name], 2)
                else:
                    logger.error(f"Column {column_name} not found in the last entry of the funds_{simulation_name} table.")
            await send_funds_embed(simulator, simulation['discord']['discord_channel_id'], start_ts, end_ts, last_fund_entry, new_fund_entry)
            await insert_fund_entry(simulator.db_manager, simulation_name, start_ts, end_ts, new_fund_entry, benefits=0.0)
        else:
            await insert_fund_entry(simulator.db_manager, simulation_name, start_ts, end_ts, last_fund_entry, benefits=0.0)
        logger.info(f"Updated fund slots for simulation {simulation_name} from {start_ts} to {end_ts}.")

    except sqlite3.Error as e:
        logger.error(f"An error occurred while updating fund slots: {e}")