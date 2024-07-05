import aiohttp
from datetime import datetime, timedelta
import sqlite3
from src.discord.configs import get_simulations_config
from src.db.manager import DatabaseManager
from src.simulation.positions import get_positions


async def simulates(simulator):
    async with aiohttp.ClientSession() as session:
        simulates_config = get_simulations_config()
        for simulation_name, simulation in simulates_config.items():
            start_ts_config = datetime.strptime(simulation["api"]["start_ts"], "%Y-%m-%d")

            if simulation["api"]["end_ts"]:
                end_ts_config = datetime.strptime(simulation["api"]["end_ts"], "%Y-%m-%d")
            else:
                end_ts_config = datetime.now()

            end_ts = start_ts_config + timedelta(days=1)
            while end_ts <= end_ts_config:
                # todo: verify here if the calculs are alrdy entered in db (avoid to calcul from start)

                positions = await get_positions(
                    simulator, 
                    simulation_name, 
                    simulation, 
                    start_ts_config, 
                    end_ts)

                # here create ts enter in db in table 'simulations' in db
                simulator.db_manager.save_simulation_data(simulation_name, start_ts_config.strftime("%Y-%m-%d"), end_ts.strftime("%Y-%m-%d"))

                for position in positions:
                    pair = position["pair"]
                    buy_date = position["buy_date"]
                    buy_price = position["buy_price"]
                    sell_date = position.get("sell_date")
                    sell_price = position.get("sell_price")

                    # check if the position already exists in the database
                    simulator.db_manager.db_cursor.execute('''SELECT id FROM positions WHERE pair = ? AND buy_date = ? AND buy_price = ? AND (sell_date = ? OR sell_date IS NULL) AND (sell_price = ? OR sell_price IS NULL)''', 
                                                           (pair, buy_date, buy_price, sell_date, sell_price))
                    existing_position = simulator.db_manager.db_cursor.fetchone()

                    if existing_position:
                        position_id = existing_position[0]
                    else:
                        # insert new position into positions table
                        simulator.db_manager.db_cursor.execute('''INSERT INTO positions (pair, buy_date, buy_price, sell_date, sell_price) 
                                                                  VALUES (?, ?, ?, ?, ?)''', 
                                                               (pair, buy_date, buy_price, sell_date, sell_price))
                        simulator.db_manager.db_connection.commit()
                        position_id = simulator.db_manager.db_cursor.lastrowid

                    # insert into simulation_positions
                    simulator.db_manager.db_cursor.execute('''INSERT OR REPLACE INTO simulation_positions (simulation_name, start_ts, end_ts, position_id) 
                                                              VALUES (?, ?, ?, ?)''', 
                                                           (simulation_name, start_ts_config.strftime("%Y-%m-%d"), end_ts.strftime("%Y-%m-%d"), position_id))
                    simulator.db_manager.db_connection.commit()

                # next ts
                end_ts += timedelta(days=1)

