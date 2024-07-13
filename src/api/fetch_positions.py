# =============================================================================
# Smartswap Simulator
# =============================================================================
# Repository: https://github.com/smartswap-org/simulator
# Author of this code: Simon
# =============================================================================
# Description of this file:
# This file contains the functions to interract with the API and get all
# old and current positions for the differents pairs and their timestamps
# intervalls (start_ts - end_ts)
# =============================================================================

from loguru import logger
import aiohttp

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
