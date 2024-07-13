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
from datetime import datetime, timedelta
from src.discord.configs import get_simulations_config
from src.simulation.positions import get_positions
from src.discord.embeds import discord 
from src.discord.integ_logs.current_positions import send_current_positions_embed
from src.db.tables import create_funds_table
from src.discord.integ_logs.position import send_position_embed
from src.db.simulation import save_simulation_data    

async def simulates(simulator):
    """
    Perform simulation for all configured strategies.
    
    simulator: Instance of Simulator class.
    """
    async with aiohttp.ClientSession() as session:
        simulates_config = get_simulations_config()  # get simulations configuration
        for simulation_name, simulation in simulates_config.items():
            await create_funds_table(simulator.db_manager, simulation_name, simulation['positions']['position_%_invest'])
            start_ts_config = datetime.strptime(simulation["api"]["start_ts"], "%Y-%m-%d")

            if simulation["api"]["end_ts"]:
                end_ts_config = datetime.strptime(simulation["api"]["end_ts"], "%Y-%m-%d")
            else:
                end_ts_config = datetime.now()

            # fetch the maximum end timestamp from simulations table
            simulator.db_manager.db_cursor.execute('''SELECT MAX(end_ts) FROM simulations 
                                                      WHERE simulation_name = ?''', 
                                                   (simulation_name,))
            last_end_ts_entry = simulator.db_manager.db_cursor.fetchone()
            
            if last_end_ts_entry and last_end_ts_entry[0]:
                last_end_ts = datetime.strptime(last_end_ts_entry[0], "%Y-%m-%d")
                end_ts = last_end_ts  
            else:
                end_ts = start_ts_config + timedelta(days=1)

            # loop through dates from start to end timestamp
            while end_ts <= end_ts_config:
                positions = await get_positions(
                    simulator, 
                    simulation_name, 
                    simulation, 
                    start_ts_config,
                    end_ts)


                # save simulation data
                save_simulation_data(simulator.db_manager, simulation_name, start_ts_config.strftime("%Y-%m-%d"), end_ts.strftime("%Y-%m-%d"))

                if len(positions) > 0:
                    # process each position
                    for position in positions:
                        pair = position["pair"]
                        buy_date = position["buy_date"]
                        buy_price = position["buy_price"]
                        sell_date = position.get("sell_date")
                        sell_price = position.get("sell_price")

                        # check if the position already exists
                        simulator.db_manager.db_cursor.execute('''SELECT id FROM positions WHERE pair = ? AND buy_date = ? AND buy_price = ? AND (sell_date = ? OR sell_date IS NULL) AND (sell_price = ? OR sell_price IS NULL)''', 
                                                            (pair, buy_date, buy_price, sell_date, sell_price))
                        existing_position = simulator.db_manager.db_cursor.fetchone()

                        if existing_position:
                            position_id = existing_position[0]
                            #await simulator.send_position_embed(simulation['discord']['discord_channel_id'], f"👨🏼‍💻 Current Position ({start_ts_config}-{end_ts})", discord.Color.orange(), position)
                        else:
                            # insert new position into positions table
                            simulator.db_manager.db_cursor.execute('''INSERT INTO positions (pair, buy_date, buy_price, sell_date, sell_price) 
                                                                    VALUES (?, ?, ?, ?, ?)''', 
                                                                (pair, buy_date, buy_price, sell_date, sell_price))
                            simulator.db_manager.db_connection.commit()
                            position_id = simulator.db_manager.db_cursor.lastrowid
                            await send_position_embed(simulator, simulation['discord']['discord_channel_id'], "🚀 Opened Position", discord.Color.brand_green(), position)


                        # insert or replace into simulation_positions table
                        simulator.db_manager.db_cursor.execute('''INSERT OR REPLACE INTO simulation_positions (simulation_name, start_ts, end_ts, position_id) 
                                                                VALUES (?, ?, ?, ?)''', 
                                                            (simulation_name, start_ts_config.strftime("%Y-%m-%d"), end_ts.strftime("%Y-%m-%d"), position_id))
                        simulator.db_manager.db_connection.commit()
                                    # send current position embed
                    await send_current_positions_embed(
                        simulator=simulator,
                        channel_id=simulation['discord']['discord_channel_id'],
                        start_ts=start_ts_config,
                        end_ts=end_ts,
                        positions=positions
                    )
                else:
                    await send_position_embed(simulator, simulation['discord']['discord_channel_id'], f"❌ No any position ({start_ts_config}-{end_ts})", discord.Color.red(), {})

                end_ts += timedelta(days=1)  # increment end timestamp by one day
