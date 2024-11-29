import os
import importlib
import aiohttp
from src.discord.configs import get_simulations_config
from src.api.fetch import fetch_ohlcv_from_api
from loguru import logger
from src.discord.integ_logs.open_position import send_open_position_embed
from src.discord.integ_logs.close_position import send_close_position_embed
from src.discord.integ_logs.fund_slot_summary import send_fund_slot_summary_embed
from src.discord.integ_logs.central_message import send_or_update_central_summary_embed
from src.db.tables import initialize_funds
from datetime import datetime, timedelta
import asyncio

def import_signals_and_indicators(strategies_folder="strategies"):
    strategies = {}
    for root, dirs, files in os.walk(strategies_folder):
        for file_name in files:
            if file_name.endswith(".py"):
                file_path = os.path.join(root, file_name)
                name_without_extension = os.path.splitext(file_name)[0]
                strategy_name = os.path.relpath(file_path, strategies_folder).replace(os.sep, '_').rsplit('.', 1)[0]
                try:
                    spec = importlib.util.spec_from_file_location(name_without_extension, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    buy_signal_func = getattr(module, 'buy_signal', None)
                    sell_signal_func = getattr(module, 'sell_signal', None)
                    indicators_class = getattr(module, 'Indicators', None)
                    if buy_signal_func and sell_signal_func and indicators_class:
                        strategies[strategy_name] = {
                            "buy_signal": buy_signal_func,
                            "sell_signal": sell_signal_func,
                            "Indicators": indicators_class
                        }
                        logger.debug(f"Imported strategy '{strategy_name}' from {file_path}")
                except Exception as e:
                    logger.error(f"Failed to import module '{strategy_name}' from {file_path}: {e}")
    logger.info(f'Strategies: {strategies}')
    return strategies

strategies = import_signals_and_indicators()

def extract_all_dates(data):
    all_dates = set()
    for pair_data in data:
        for entry in pair_data['data']:
            date_str = entry[0]
            all_dates.add(datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S"))
    return sorted(all_dates)

def str_to_datetime(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S") if date_str else None

def preprocess_data(pair_data):
    return {datetime.strptime(entry[0], "%Y-%m-%d %H:%M:%S"): i for i, entry in enumerate(pair_data['data'])}

def get_index_for_date(preprocessed_data, target_date, pair_name):
    if isinstance(target_date, datetime):
        target_date_key = target_date
    elif isinstance(target_date, datetime.date):
        target_date_key = datetime.combine(target_date, datetime.min.time())
    else:
        logger.error("Invalid target_date type: %s", type(target_date))
        return None
    
    index = preprocessed_data.get(target_date_key, None)
    
    if index is None:
        logger.error(f'No index found for date {target_date_key} ({pair_name})')
    
    return index

async def simulates(simulator):
    async with aiohttp.ClientSession() as session:
        simulations_config = get_simulations_config()
        for simulation_name, simulation in simulations_config.items():
            logger.info(f"Starting simulation: {simulation_name}")
            
            # Calculate fund slots and initial capital
            max_fund_slots = 100 // int(simulation['positions']['position_%_invest'])
            initial_capital = float(simulation['wallet']['invest_capital'])
            initial_capital_per_slot = initial_capital / max_fund_slots
            
            # Initialize funds
            await initialize_funds(simulator.db_manager, simulation_name, max_fund_slots, initial_capital_per_slot)

            # Fetch OHLCV data
            data = await fetch_ohlcv_from_api(simulation)
            pairs_list = simulation['api']['pairs_list']

            most_recent_date_str = simulator.positions.get_most_recent_date(simulation_name)
            most_recent_date = str_to_datetime(most_recent_date_str)

            start_ts = simulation['api'].get('start_ts')
            end_ts = simulation['api'].get('end_ts')

            start_date = str_to_datetime(start_ts) if start_ts else None
            end_date = str_to_datetime(end_ts) if end_ts else None

            if start_date and (most_recent_date is None or most_recent_date < start_date):
                most_recent_date = start_date
                logger.info(f"Adjusted start date to {start_date.strftime('%Y-%m-%d %H:%M:%S')}")

            all_dates = extract_all_dates(data)
            filtered_dates = [date for date in all_dates if most_recent_date is None or date > most_recent_date - timedelta(days=1)]
            if end_date:
                filtered_dates = [date for date in filtered_dates if date <= end_date]

            closed_positions_ids = set()
            start_time = asyncio.get_event_loop().time()

            for target_date in filtered_dates:
                await send_or_update_central_summary_embed(simulator, simulation['discord'].get('discord_channel_id'), simulation_name)

                current_time = asyncio.get_event_loop().time()
                elapsed_time = current_time - start_time

                if elapsed_time >= 10:
                    await asyncio.sleep(1)
                    start_time = asyncio.get_event_loop().time()

                if end_date and target_date > end_date:
                    logger.info(f"Stopping simulation as target date {target_date.strftime('%Y-%m-%d %H:%M:%S')} exceeds end date {end_date.strftime('%Y-%m-%d %H:%M:%S')}")
                    break

                logger.info(f"Processing date: {target_date.strftime('%Y-%m-%d %H:%M:%S')}")

                for pair_name, pair_data in zip(pairs_list, data):
                    await asyncio.sleep(0)  # Yield control to the event loop
                    preprocessed_data = preprocess_data(pair_data)
                    index = get_index_for_date(preprocessed_data, target_date, pair_name)
                    if index is None:
                        continue

                    indicators = strategies[simulation['api']['strategy']]['Indicators'](pair_data['data']).indicators

                    open_positions = simulator.positions.get_open_positions_by_pair(simulation_name, pair_name)
                    
                    if open_positions:
                        for pos in open_positions:
                            if pos['id'] in closed_positions_ids:
                                continue
                            sell_signal, sell_price = strategies[simulation['api']['strategy']]['sell_signal'](pos, pair_data['data'], index, indicators)
                            if sell_signal > 0:
                                sell_date = pair_data['data'][index][0]
                                sell_price = sell_price
                                sell_index = index
                                simulator.positions.close_position(
                                    pos['id'], sell_date, sell_price, sell_index, sell_signal
                                )
                                closed_positions_ids.add(pos['id'])
                                logger.info(f"Closed position {pos['id']} for {pair_name} on {sell_date} at price {sell_price}")
                                await send_close_position_embed(simulator, simulation['discord']['discord_channel_id'], pos['id'])
                                await send_fund_slot_summary_embed(simulator, simulation['discord']['discord_channel_id'], pos['id'])
                    free_fund_slots = simulator.positions.get_free_fund_slots(simulation_name, max_fund_slots)
                    if free_fund_slots:
                        buy_signal, buy_price = strategies[simulation['api']['strategy']]['buy_signal'](None, pair_data['data'], index, indicators)
                        if buy_signal > 0:
                            fund_slot = free_fund_slots.pop(0)  
                            buy_date = pair_data['data'][index][0]
                            buy_price = buy_price
                            position_id = simulator.positions.create_position(
                                simulation_name, pair_name, buy_date, buy_price, index, fund_slot, buy_signal
                            )
                            logger.info(f"Opened position {position_id} for {pair_name} on {buy_date} at price {buy_price} with fund slot {fund_slot}")
                            await send_open_position_embed(simulator, simulation['discord']['discord_channel_id'], position_id)
    logger.info("Simulation completed.")
    logger.info("")