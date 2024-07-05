import aiohttp
from datetime import datetime

# to do here : fetch for every pairs the current positions and find the best one 

async def get_positions(
                    simulator, 
                    simulation_name, 
                    simulation, 
                    start_ts_config, 
                    end_ts):
    
    pair = "Binance_DOGEUSDT_1d"
    url = f"http://127.0.0.1:5000/QTSBE/{pair}/{simulation['api']['strategy']}?start_ts={start_ts_config.strftime('%Y-%m-%d')}&end_ts={end_ts.strftime('%Y-%m-%d')}&multi_positions={simulation['api']['multi_positions']}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                response_json = await response.json()  # Utilisez await pour obtenir le JSON de la réponse
                positions = response_json["result"][2] # 0 = indicators, 1 = all old positions (ended) , 2 = current position
                for position in positions:
                    position['pair'] = pair
            else:
                positions = []
                print(f"Failed to fetch data from {url}, status code: {response.status}")

    return positions
