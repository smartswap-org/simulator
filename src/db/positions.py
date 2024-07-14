# =============================================================================
# Smartswap Simulator
# =============================================================================
# Repository: https://github.com/smartswap-org/simulator
# Author of this code: Simon
# =============================================================================
# Description of this file:
# This file contains the functions used to interract with database to
# fetch, update, save positions.
# =============================================================================

import discord 
import sqlite3
from loguru import logger
from src.discord.integ_logs.position import send_position_embed


async def fetch_positions_from_database(db_manager, simulation_name, previous_end_ts):
    """
    Fetch positions from the database for a specific simulation and end timestamp.
    
    simulator: Instance of Simulator class.
    simulation_name: Name of the simulation.
    previous_end_ts: Previous end timestamp for fetching positions.
    
    return: List of positions fetched from the database.
    """
    db_manager.db_cursor.execute(
        '''SELECT p.*, p.buy_signals, p.sell_signals
           FROM positions p
           JOIN simulation_positions sp ON p.id = sp.position_id 
           WHERE sp.simulation_name = ? 
           AND sp.end_ts = ?''',
        (simulation_name, previous_end_ts.strftime("%Y-%m-%d"))
    )
    return db_manager.db_cursor.fetchall()

async def update_positions_in_database(simulator, simulation_name, simulation, previous_position, old_position):
    """
    Update positions in the database based on new data.
    
    simulator: Instance of Simulator class.
    simulation_name: Name of the simulation.
    simulation: Simulation configuration dictionary.
    previous_position: Updated position data.
    old_position: Old position data.
    """
    try:
        simulator.db_manager.db_cursor.execute(
            '''UPDATE positions 
               SET sell_date = ?, sell_price = ?, 
                   buy_signals = ?, sell_signals = ?, 
                   buy_index = ?, sell_index = ?, 
                   position_duration = ?, ratio = ?
               WHERE id = ?''', 
            (previous_position['sell_date'], previous_position['sell_price'], 
             previous_position['buy_signals'], previous_position['sell_signals'], 
             previous_position['buy_index'], previous_position['sell_index'], 
             previous_position['position_duration'], previous_position['ratio'], 
             old_position[0])
        )
        simulator.db_manager.db_connection.commit()
        
        # fetch the updated position from the database
        simulator.db_manager.db_cursor.execute(
            '''SELECT pair, buy_date, buy_price, sell_date, sell_price, buy_signals, sell_signals, ratio, position_duration
               FROM positions
               WHERE id = ?''', 
            (old_position[0],)
        )
        updated_position = simulator.db_manager.db_cursor.fetchone()
        if updated_position:
            position = {
                'id': old_position[0],
                'pair': updated_position[0],
                'buy_date': updated_position[1],
                'buy_price': updated_position[2],
                'sell_date': updated_position[3],
                'sell_price': updated_position[4],
                'buy_signals': updated_position[5],
                'sell_signals': updated_position[6],
                'ratio': updated_position[7],
                'position_duration': updated_position[8]
            }
            await send_position_embed(simulator, simulation['discord']['discord_channel_id'], "🎊 Closed Position", discord.Color.pink(), position)
        
        logger.debug(f"Position updated in database: {simulation_name}, {old_position}")
    except sqlite3.Error as e:
        logger.error(f"Error updating position in database: {e}")
 
async def get_positions_for_simulation(db_manager, simulation_name, start_ts, end_ts):
    """
    Retrieve positions for a given simulation from the database.
    
    simulation_name: Name of the simulation.
    start_ts: Start timestamp of the simulation.
    end_ts: End timestamp of the simulation.
    
    return: A list of positions or None if an error occurred.
    """
    try:
        db_manager.db_cursor.execute('''SELECT DISTINCT p.pair, p.buy_date, p.buy_price, p.sell_date, p.sell_price,
                                           p.buy_index, p.sell_index, p.position_duration, p.ratio,
                                           p.buy_signals, p.sell_signals
                                  FROM positions p
                                  INNER JOIN simulation_positions sp ON p.id = sp.position_id
                                  WHERE sp.simulation_name = ? AND sp.start_ts >= ? AND sp.end_ts <= ?''',
                               (simulation_name, start_ts, end_ts))
        positions = db_manager.db_cursor.fetchall()  # fetch all matching records
        return positions  # return the list of positions
    except sqlite3.Error as e:
        logger.error(f"An error occurred while retrieving positions for simulation: {e}")
        return None  # return None if an error occurred

async def save_position(db_manager, pair, buy_date, buy_price, sell_date, sell_price, buy_index, sell_index, position_duration, ratio, buy_signals, sell_signals, fund_slot):
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
        db_manager.db_cursor.execute('''SELECT id FROM positions WHERE pair = ? AND buy_date = ? AND buy_price = ? AND sell_date = ? AND sell_price = ?''', 
                               (pair, buy_date, buy_price, sell_date, sell_price))
        position = db_manager.db_cursor.fetchone()  # fetch one matching record
        if position:
            position_id = position[0]  # get the position ID
        else:
            db_manager.db_cursor.execute('''INSERT INTO positions (pair, buy_date, buy_price, sell_date, sell_price, buy_index, sell_index, position_duration, ratio, buy_signals, sell_signals, fund_slot) 
                                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                   (pair, buy_date, buy_price, sell_date, sell_price, buy_index, sell_index, position_duration, ratio, buy_signals, sell_signals, fund_slot))
            db_manager.db_connection.commit()  # commit the changes
            position_id = db_manager.db_cursor.lastrowid  # get the ID of the last inserted row
        return position_id  # return the position ID
    except sqlite3.Error as e:
        logger.error(f"An error occurred while saving position: {e}")
        return None  # return None if an error occurred
