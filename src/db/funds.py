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
