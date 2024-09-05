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

import aiohttp
from loguru import logger

async def fetch_ohlcv_from_api(simulation):
    """
    Fetch positions from an API endpoint for a specific simulation and time range.
    
    simulation: Simulation configuration dictionary.
    start_ts_config: Start timestamp for the API query.
    end_ts: End timestamp for the API query.

    return: Tuple containing current positions fetched from API and previous positions.
    """
    try:
        pairs = list(simulation['api']['pairs_list'])
        pairs_data = []

        async with aiohttp.ClientSession() as session:
            for pair in pairs:
                url = f"http://127.0.0.1:5000/QTSBE/{pair}/{simulation['api']['strategy']}?details=True"

                async with session.get(url) as response:
                    if response.status == 200:
                        response_json = await response.json()
                        pairs_data.extend([response_json])
                    else:
                        logger.error(f"Failed to fetch data from {url}, status code: {response.status}")

        return pairs_data

    except Exception as e:
        logger.error(f"Error fetching positions from API: {e}")
        return [], []