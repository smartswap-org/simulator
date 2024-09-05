# =============================================================================
# Smartswap Simulator
# =============================================================================
# Repository: https://github.com/smartswap-org/simulator
# Author of this code: Simon
# =============================================================================
# Description of this file:
# This file contains the simulates function which handles the simulation process
# by fetching data from APIs, processing positions, and saving them into the database.
# =============================================================================

import aiohttp
from src.discord.configs import get_simulations_config
from src.api.fetch import fetch_ohlcv_from_api
from datetime import datetime

async def simulates(simulator):
    async with aiohttp.ClientSession() as session:
        simulates_config = get_simulations_config()  # get simulations configuration
        for simulation_name, simulation in simulates_config.items():
            most_recent_date = simulator.positions.get_most_recent_date(simulation_name)
            #if most_recent_date:
            #    start_ts = most_recent_date
            #else:
            #    start_ts = simulation.get('api')['start_ts']
            start_ts = simulation.get('api')['start_ts']
            data = await fetch_ohlcv_from_api(simulation)
            pairs_list = simulation.get('api')['pairs_list']
            for idx, pair_data in enumerate(data):
                pair_name = pairs_list[idx]
                open_positions = simulator.positions.get_open_positions_by_pair(simulation_name, pair_name)
                max_index = simulator.positions.get_max_index_for_pair(simulation_name, pair_name)
                start_index = 0
                if max_index != None: start_index = max_index
    return
