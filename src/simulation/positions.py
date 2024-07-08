import json
import aiohttp
from datetime import timedelta

async def fetch_positions_from_database(simulator, simulation_name, previous_end_ts):
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
    pair = "Binance_SOLUSDT_1d"
    url = f"http://127.0.0.1:5000/QTSBE/{pair}/{simulation['api']['strategy']}?start_ts={start_ts_config.strftime('%Y-%m-%d')}&end_ts={end_ts.strftime('%Y-%m-%d')}&multi_positions={simulation['api']['multi_positions']}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_json = await response.json()
                current_positions = response_json["result"][2]
                return current_positions, response_json["result"][1]
            else:
                print(f"Failed to fetch data from {url}, status code: {response.status}")
                return [], []

async def update_positions_in_database(simulator, previous_position, old_position):
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

async def get_positions(simulator, simulation_name, simulation, start_ts_config, end_ts):
    previous_end_ts = end_ts - timedelta(days=2)
    positions = []

    if previous_end_ts >= start_ts_config:
        old_positions = await fetch_positions_from_database(simulator, simulation_name, previous_end_ts)

        current_positions, previous_positions = await fetch_positions_from_api(simulation, start_ts_config, end_ts)

        for position in current_positions:
            position['pair'] = position.get('pair', "Binance_SOLUSDT_1d")
            position['buy_signals'] = json.dumps(position.get('buy_signals', []))
            position['sell_signals'] = json.dumps(position.get('sell_signals', []))
            positions.append(position)

        for old_position in old_positions:
            found = False
            for current_position in current_positions:
                if (old_position[1] == current_position.get('pair') and 
                    old_position[2] == current_position['buy_date'] and 
                    old_position[3] == current_position['buy_price'] and 
                    old_position[4] is None):
                    
                    positions.append(current_position)
                    found = True
                    break

            if not found:
                for previous_position in previous_positions:
                    if (previous_position['buy_date'] == old_position[2] and 
                        previous_position['buy_price'] == old_position[3]):
                        previous_position['buy_signals'] = json.dumps(previous_position.get('buy_signals', []))
                        previous_position['sell_signals'] = json.dumps(previous_position.get('sell_signals', []))
                        await update_positions_in_database(simulator, previous_position, old_position)
                        break

        positions.extend([
            current_position for current_position in current_positions 
            if not any(old_position[1] == current_position.get('pair') and
                       old_position[2] == current_position['buy_date'] and
                       old_position[3] == current_position['buy_price'] and
                       old_position[4] is None
                       for old_position in old_positions)
        ])

    else:
        current_positions, _ = await fetch_positions_from_api(simulation, start_ts_config, end_ts)
        positions = current_positions

    return positions
