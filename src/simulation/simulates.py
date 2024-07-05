# simulates.py
import aiohttp
from datetime import datetime, timedelta
import sqlite3
from src.discord.configs import get_simulations_config
from src.db.manager import DatabaseManager

async def simulates(simulator):
    async with aiohttp.ClientSession() as session:
        simulates_config = get_simulations_config()
        for simulation_name, simulation in simulates_config.items():
            start_ts = datetime.strptime(simulation["api"]["start_ts"], "%Y-%m-%d")
            end_ts_config = simulation["api"]["end_ts"]
            end_ts = datetime.strptime(end_ts_config, "%Y-%m-%d") if end_ts_config else datetime.now()

            current_date = start_ts
            while current_date <= end_ts:
                end_ts_str = current_date.strftime("%Y-%m-%d")
                for pair in simulation["api"]["pairs_list"]:
                    url = f"http://127.0.0.1:5000/QTSBE/{pair}/{simulation['api']['strategy']}?start_ts={start_ts.strftime('%Y-%m-%d')}&end_ts={end_ts_str}&multi_positions={simulation['api']['multi_positions']}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            response_json = await response.json()
                            positions = response_json["result"][1]
                        else:
                            positions = []
                            print(f"Failed to fetch data from {url}, status code: {response.status}")

                    simulator.db_manager.save_simulation_data(simulation_name, start_ts.strftime("%Y-%m-%d"), current_date.strftime("%Y-%m-%d"))

                    for position in positions:
                        simulator.db_manager.save_position(simulation_name, start_ts.strftime("%Y-%m-%d"), current_date.strftime("%Y-%m-%d"), 
                                                          pair, position['buy_date'], position['buy_price'], 
                                                          position.get('sell_date'), position.get('sell_price'))

                    previous_positions = simulator.db_manager.get_positions_for_simulation(simulation_name, start_ts.strftime("%Y-%m-%d"), (current_date - timedelta(days=1)).strftime("%Y-%m-%d"))
                    current_positions = simulator.db_manager.get_positions_for_simulation(simulation_name, start_ts.strftime("%Y-%m-%d"), current_date.strftime("%Y-%m-%d"))

                    for prev_pos in previous_positions:
                        position_found = False
                        for curr_pos in current_positions:
                            if prev_pos[0] == curr_pos[0]:  # Compare pairs
                                position_found = True
                                break
                        if not position_found:
                            # Position is sold
                            simulator.update_position_sell_info(simulation_name, start_ts.strftime("%Y-%m-%d"), prev_pos[1], prev_pos[2], current_date.strftime("%Y-%m-%d"))

                current_date += timedelta(days=1)
