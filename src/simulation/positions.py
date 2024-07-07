import aiohttp
from datetime import timedelta

async def get_positions(
                    simulator, 
                    simulation_name, 
                    simulation, 
                    start_ts_config, 
                    end_ts_config, 
                    end_ts):
    
    previous_end_ts = end_ts - timedelta(days=2)
    positions = []
    print(start_ts_config, previous_end_ts, end_ts, (previous_end_ts >= start_ts_config))
    if previous_end_ts >= start_ts_config: 
        simulator.db_manager.db_cursor.execute('''SELECT positions.*
                                                  FROM positions 
                                                  JOIN simulation_positions ON positions.id = simulation_positions.position_id 
                                                  WHERE simulation_positions.simulation_name = ? 
                                                  AND simulation_positions.end_ts = ?''', 
                                               (simulation_name, previous_end_ts.strftime("%Y-%m-%d")))
        old_positions = simulator.db_manager.db_cursor.fetchall()

        pair = "Binance_DOGEUSDT_1d"
        url = f"http://127.0.0.1:5000/QTSBE/{pair}/{simulation['api']['strategy']}?start_ts={start_ts_config.strftime('%Y-%m-%d')}&end_ts={end_ts.strftime('%Y-%m-%d')}&multi_positions={simulation['api']['multi_positions']}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    response_json = await response.json()
                    current_positions = response_json["result"][2]  # 0 = indicators, 1 = all old positions (ended), 2 = current position
                    for position in current_positions:
                        position['pair'] = pair
                else:
                    current_positions = []
                    print(f"Failed to fetch data from {url}, status code: {response.status}")

        for old_position in old_positions:
            found = False
            for current_position in current_positions:
                print(old_position)
                if (old_position[1] == current_position['pair'] and 
                    old_position[2] == current_position['buy_date'] and 
                    old_position[3] == current_position['buy_price'] and 
                    old_position[4] is None):
                    
                    positions.append(current_position)
                    found = True
                    break

            if not found:
                simulator.db_manager.db_cursor.execute('''UPDATE positions 
                                                          SET sell_date = ?, sell_price = ? 
                                                          WHERE id = ?''', 
                                                       (end_ts.strftime("%Y-%m-%d"), old_position[5], old_position[0]))
                simulator.db_manager.db_connection.commit()

        for current_position in current_positions:
            if not any(old_position[1] == current_position['pair'] and
                       old_position[2] == current_position['buy_date'] and
                       old_position[3] == current_position['buy_price'] and
                       old_position[4] is None
                       for old_position in old_positions):
                positions.append(current_position)

    else: 
        pair = "Binance_DOGEUSDT_1d"
        url = f"http://127.0.0.1:5000/QTSBE/{pair}/{simulation['api']['strategy']}?start_ts={start_ts_config.strftime('%Y-%m-%d')}&end_ts={end_ts.strftime('%Y-%m-%d')}&multi_positions={simulation['api']['multi_positions']}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    response_json = await response.json()
                    positions = response_json["result"][2]  # 0 = indicators, 1 = all old positions (ended), 2 = current position
                    for position in positions:
                        position['pair'] = pair
                else:
                    positions = []
                    print(f"Failed to fetch data from {url}, status code: {response.status}")
    print(positions)
    return positions
