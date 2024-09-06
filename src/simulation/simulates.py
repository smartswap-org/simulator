import os 
import importlib
import aiohttp
from src.discord.configs import get_simulations_config
from src.api.fetch import fetch_ohlcv_from_api
from QTSBE.api.algo.indicators.rsi import get_RSI
from loguru import logger
from src.discord.integ_logs.open_position import send_open_position_embed
from src.discord.integ_logs.close_position import send_close_position_embed

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
                        logger.debug(f"Successfully imported 'buy_signal', 'sell_signal', and 'Indicators' from {file_path} as {strategy_name}")
                    else:
                        logger.warning(f"Module '{strategy_name}' does not contain 'buy_signal', 'sell_signal', and 'Indicators'")

                except Exception as e:
                    logger.error(f"Failed to import module '{strategy_name}' from {file_path}: {e}")
    logger.info(f'Strategies: {strategies}')    
    return strategies

strategies = import_signals_and_indicators()

async def simulates(simulator):
    async with aiohttp.ClientSession() as session:
        simulations_config = get_simulations_config()

        for simulation_name, simulation in simulations_config.items():
            logger.info(f"Starting simulation: {simulation_name}")

            data = await fetch_ohlcv_from_api(simulation)
            pairs_list = simulation['api']['pairs_list']
            max_fund_slots = 100 // int(simulation['positions']['position_%_invest'])

            for pair_name, pair_data in zip(pairs_list, data):
                logger.info(f"Processing pair: {pair_name}")

                open_positions = simulator.positions.get_open_positions_by_pair(simulation_name, pair_name)
                start_index = simulator.positions.get_max_index_for_pair(simulation_name, pair_name) or 0
                prices = [float(entry[1].replace(',', '')) for entry in pair_data['data']]
                rsi = get_RSI(prices, 14)
                indicators = strategies[simulation['api']['strategy']]['Indicators'](prices)

                for i in range(start_index, len(prices)):
                    if rsi[i] is None:
                        continue
                    
                    if not open_positions:
                        free_fund_slots = simulator.positions.get_free_fund_slots(simulation_name, pair_name, max_fund_slots)
                        if free_fund_slots:
                            fund_slot = free_fund_slots[0]
                            buy_signal = strategies[simulation['api']['strategy']]['buy_signal'](None, prices, i, indicators)
                            if buy_signal > 0:
                                buy_date = pair_data['data'][i][0]
                                buy_price = prices[i]
                                buy_index = i
                                buy_signal = buy_signal
                                position_id = simulator.positions.create_position(
                                    simulation_name, pair_name, buy_date, buy_price, buy_index, fund_slot, buy_signal
                                )
                                logger.info(f"Opened position {position_id} for {pair_name} on {buy_date} at price {buy_price} with fund slot {fund_slot}")
                                open_positions = simulator.positions.get_open_positions_by_pair(simulation_name, pair_name) 
                                await send_open_position_embed(simulator, simulation['discord']['discord_channel_id'], position_id)
                    else:
                        open_position = open_positions[0]  # Assuming only one open position
                        sell_signal = strategies[simulation['api']['strategy']]['sell_signal'](open_position, prices, i, indicators)
                        if sell_signal > 0:
                            sell_date = pair_data['data'][i][0]
                            sell_price = prices[i]
                            sell_index = i
                            sell_signal = sell_signal
                            simulator.positions.close_position(
                                open_position['id'], sell_date, sell_price, sell_index, sell_signal
                            )
                            logger.info(f"Closed position {open_position['id']} for {pair_name} on {sell_date} at price {sell_price}")
                            open_positions = simulator.positions.get_open_positions_by_pair(simulation_name, pair_name)
                            await send_close_position_embed(simulator, simulation['discord']['discord_channel_id'], open_position['id'])

    logger.info("Simulation completed.")