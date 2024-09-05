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
from QTSBE.api.algo.indicators.rsi import get_RSI
from loguru import logger

async def simulates(simulator):
    async with aiohttp.ClientSession() as session:
        simulates_config = get_simulations_config() 
        for simulation_name, simulation in simulates_config.items():
            most_recent_date = simulator.positions.get_most_recent_date(simulation_name)
            start_ts = simulation.get('api')['start_ts']
            data = await fetch_ohlcv_from_api(simulation)
            pairs_list = simulation.get('api')['pairs_list']
            
            for idx, pair_data in enumerate(data):
                pair_name = pairs_list[idx]
                open_positions = simulator.positions.get_open_positions_by_pair(simulation_name, pair_name)
                max_index_positions = simulator.positions.get_max_index_for_pair(simulation_name, pair_name)
                start_index = max_index_positions if max_index_positions is not None else 0
                max_index = len(pair_data['data']) - 1

                prices = [float(entry[1].replace(',', '')) for entry in pair_data['data']]
                rsi = get_RSI(prices, 14)
                #logger.debug(f"{pair_name} open_positions: {open_positions}")
                logger.debug(f"{pair_name} start_index: {start_index} / max_index: {max_index}")
                for i in range(start_index, max_index):
                    if rsi[i] is None:
                        continue 

                    if not open_positions:
                        if rsi[i] < 40:
                            buy_date = pair_data['data'][i][0]
                            buy_price = prices[i]
                            buy_index = i
                            fund_slot = 1.0  
                            buy_signals = f"RSI: {rsi[i]}"
                            position_id = simulator.positions.create_position(
                                simulation_name, pair_name, buy_date, buy_price, buy_index, fund_slot, buy_signals
                            )
                            logger.info(f"Opened position {position_id} for {pair_name} on {buy_date} at price {buy_price}")
                            open_positions = simulator.positions.get_open_positions_by_pair(simulation_name, pair_name)  
                    else:
                        position = open_positions[0]  
                        if rsi[i] > 50 and prices[i] / float(position[4]) > 1.10:  
                            sell_date = pair_data['data'][i][0]
                            sell_price = prices[i]
                            sell_index = i
                            sell_signals = "{RSI: " + str(round(rsi[i], 3)) + "}"
                            simulator.positions.close_position(
                                position[1], sell_date, sell_price, sell_index, sell_signals
                            )
                            logger.info(f"Closed position {position[1]} for {pair_name} on {sell_date} at price {sell_price}")
                            open_positions = simulator.positions.get_open_positions_by_pair(simulation_name, pair_name)  
    return