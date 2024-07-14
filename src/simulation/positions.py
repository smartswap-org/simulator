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
from datetime import timedelta
from datetime import datetime
from loguru import logger
from src.db.positions import fetch_positions_from_database, update_positions_in_database
from src.api.fetch_positions import fetch_positions_from_api

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
        max_positions = int(100/int(simulation['positions']['position_%_invest']))
        fund_slots = [False] * max_positions
        previous_end_ts = end_ts - timedelta(days=1)
        positions_dict = {}  

        # check if there are previous positions to consider
        if previous_end_ts- timedelta(days=1) >= start_ts_config:
           
            old_positions = await fetch_positions_from_database(simulator.db_manager, simulation_name, previous_end_ts)
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
                        fund_slots[int(old_position[10])-1] = True
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

        return positions, fund_slots

    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        return [], []
