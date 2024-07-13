import discord 
from loguru import logger
import sqlite3

async def fetch_positions_from_database(simulator, simulation_name, previous_end_ts):
    """
    Fetch positions from the database for a specific simulation and end timestamp.
    
    simulator: Instance of Simulator class.
    simulation_name: Name of the simulation.
    previous_end_ts: Previous end timestamp for fetching positions.
    
    return: List of positions fetched from the database.
    """
    simulator.db_manager.db_cursor.execute(
        '''SELECT p.*, p.buy_signals, p.sell_signals
           FROM positions p
           JOIN simulation_positions sp ON p.id = sp.position_id 
           WHERE sp.simulation_name = ? 
           AND sp.end_ts = ?''',
        (simulation_name, previous_end_ts.strftime("%Y-%m-%d"))
    )
    return simulator.db_manager.db_cursor.fetchall()

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
            await simulator.send_position_embed(simulation['discord']['discord_channel_id'], "🎊 Closed Position", discord.Color.pink(), position)
        
        logger.debug(f"Position updated in database: {simulation_name}, {old_position}")
    except sqlite3.Error as e:
        logger.error(f"Error updating position in database: {e}")