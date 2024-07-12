# =============================================================================
# Smartswap Simulator
# =============================================================================
# Repository: https://github.com/smartswap-org/simulator
# Author of this code: Simon
# =============================================================================
# Description of this file:
# Give all positions from a start_ts to a end_ts considering old positions and
# update them if more datas available.
# =============================================================================

import json
import aiohttp
from datetime import timedelta
import sqlite3
from datetime import datetime
from src.discord.embeds import discord
from src.discord.configs import get_simulations_config
from loguru import logger

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

async def fetch_positions_from_api(simulation, start_ts_config, end_ts):
    """
    Fetch positions from an API endpoint for a specific simulation and time range.
    
    simulation: Simulation configuration dictionary.
    start_ts_config: Start timestamp for the API query.
    end_ts: End timestamp for the API query.

    return: Tuple containing current positions fetched from API and previous positions.
    """
    try:
        pairs = list(simulation['api']['pairs_list'])
        all_current_positions = []
        all_old_positions = []

        async with aiohttp.ClientSession() as session:
            for pair in pairs:
                url = f"http://127.0.0.1:5000/QTSBE/{pair}/{simulation['api']['strategy']}?start_ts={start_ts_config.strftime('%Y-%m-%d')}&end_ts={end_ts.strftime('%Y-%m-%d')}&multi_positions={simulation['api']['multi_positions']}"

                async with session.get(url) as response:
                    if response.status == 200:
                        response_json = await response.json()
                        old_positions = response_json["result"][1]
                        current_positions = response_json["result"][2]
                        
                        for position in old_positions:
                            position['pair'] = pair
                        for position in current_positions:
                            position['pair'] = pair
                        
                        all_old_positions.extend(old_positions)
                        all_current_positions.extend(current_positions)
                    else:
                        logger.error(f"Failed to fetch data from {url}, status code: {response.status}")

        return all_current_positions, all_old_positions

    except Exception as e:
        logger.error(f"Error fetching positions from API: {e}")
        return [], []

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

async def get_positions(simulator, simulation_name, simulation, start_ts_config, end_ts):
    """
    Fetch positions for a specific simulation and time range,
    combining data from API and database.

    simulator: Instance of Simulator class.
    simulation_name: Name of the simulation.
    simulation: Simulation configuration dictionary.
    start_ts_config: Start timestamp for the position fetch.
    end_ts: End timestamp for the position fetch.

    return: List of positions fetched and processed.
    """
    try:
        max_positions = 100/int(simulation['positions']['position_%_invest'])
        previous_end_ts = end_ts - timedelta(days=1)
        positions_dict = {}  

        # check if there are previous positions to consider
        if previous_end_ts- timedelta(days=1) >= start_ts_config:
           
            old_positions = await fetch_positions_from_database(simulator, simulation_name, previous_end_ts)
            current_positions, previous_positions = await fetch_positions_from_api(simulation, start_ts_config, end_ts)

            # this is usefull if we wants to send every positions (like signals) on discord 
            # and not a max of 5 on same time for ex
            if simulation['positions']['position_%_invest'] == "-1": max_positions = len(current_positions) 

            # update old positions based on new data
            for old_position in old_positions:
                found = False
                for current_position in current_positions:
                    if (old_position[1] == current_position.get('pair') and 
                        old_position[2] == current_position['buy_date'] and 
                        old_position[3] == current_position['buy_price'] and 
                        old_position[4] is None):
                        
                        positions_dict[(current_position['pair'], current_position['buy_date'], current_position['buy_price'])] = current_position
                        found = True
                        break

                if not found:
                    for previous_position in previous_positions:
                        if (previous_position['buy_date'] == old_position[2] and 
                            previous_position['buy_price'] == old_position[3]):
                            previous_position['buy_signals'] = json.dumps(previous_position.get('buy_signals', []))
                            previous_position['sell_signals'] = json.dumps(previous_position.get('sell_signals', []))
                            await update_positions_in_database(simulator, simulation_name, simulation, previous_position, old_position)
                            break
            #print(start_ts_config, end_ts, len(old_positions), len(current_positions), len(positions_dict))
            # process current positions from API
            for current_position in current_positions:
                if len(positions_dict) < max_positions: 
                    key = (current_position['pair'], current_position['buy_date'], current_position['buy_price'])
                    
                    # check if this position already exists
                    if key not in positions_dict:
                        if datetime.strptime(current_position['buy_date'], "%Y-%m-%d") == end_ts: # ensure that we dont take a old current position
                            current_position['buy_signals'] = json.dumps(current_position.get('buy_signals', []))
                            current_position['sell_signals'] = json.dumps(current_position.get('sell_signals', []))
                            positions_dict[key] = current_position                    
        else:
            # fetch positions directly from API if no previous positions
            current_positions, _ = await fetch_positions_from_api(simulation, start_ts_config, end_ts)
            for current_position in current_positions:
                if len(positions_dict) < max_positions: 
                    key = (current_position['pair'], current_position['buy_date'], current_position['buy_price'])
                    if key not in positions_dict:
                        if datetime.strptime(current_position['buy_date'], "%Y-%m-%d") == end_ts: # ensure that we dont take a old current position
                            current_position['buy_signals'] = json.dumps(current_position.get('buy_signals', []))
                            current_position['sell_signals'] = json.dumps(current_position.get('sell_signals', []))
                            positions_dict[key] = current_position

        # convert dictionary to list of positions
        positions = list(positions_dict.values())

        return positions

    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        return []
