import sqlite3
from loguru import logger

class DatabaseManager:
    def __init__(self, db_path='simulator.db'):
        self.db_connection = sqlite3.connect(db_path)
        self.db_cursor = self.db_connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS simulations (
                                  simulation_name TEXT,
                                  start_ts TEXT,
                                  end_ts TEXT,
                                  PRIMARY KEY (simulation_name, start_ts, end_ts))''')

        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS positions (
                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  pair TEXT,
                                  buy_date TEXT,
                                  buy_price REAL,
                                  sell_date TEXT,
                                  sell_price REAL,
                                  buy_index INTEGER,
                                  sell_index INTEGER,
                                  position_duration INTEGER,
                                  ratio REAL,
                                  buy_signals TEXT,
                                  sell_signals TEXT)''')

        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS simulation_positions (
                                  simulation_name TEXT,
                                  start_ts TEXT,
                                  end_ts TEXT,
                                  position_id INTEGER,
                                  FOREIGN KEY(simulation_name, start_ts, end_ts) REFERENCES simulations(simulation_name, start_ts, end_ts),
                                  FOREIGN KEY(position_id) REFERENCES positions(id),
                                  PRIMARY KEY (simulation_name, start_ts, end_ts, position_id))''')

        self.db_connection.commit()

    def save_simulation_data(self, simulation_name, start_ts, end_ts):
        try:
            self.db_cursor.execute('''INSERT OR REPLACE INTO simulations (simulation_name, start_ts, end_ts) 
                                      VALUES (?, ?, ?)''', 
                                   (simulation_name, start_ts, end_ts))
            self.db_connection.commit()
            logger.debug(f"Simulation data saved: {simulation_name}, {start_ts} to {end_ts}")
        except sqlite3.Error as e:
            logger.error(f"An error occurred while saving simulation data: {e}")

    def save_position(self, pair, buy_date, buy_price, sell_date, sell_price, buy_index, sell_index, position_duration, ratio, buy_signals, sell_signals):
        try:
            # Check if the position already exists
            self.db_cursor.execute('''SELECT id FROM positions WHERE pair = ? AND buy_date = ? AND buy_price = ? AND sell_date = ? AND sell_price = ?''', 
                                   (pair, buy_date, buy_price, sell_date, sell_price))
            position = self.db_cursor.fetchone()
            if position:
                position_id = position[0]
            else:
                self.db_cursor.execute('''INSERT INTO positions (pair, buy_date, buy_price, sell_date, sell_price, buy_index, sell_index, position_duration, ratio, buy_signals, sell_signals) 
                                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                                       (pair, buy_date, buy_price, sell_date, sell_price, buy_index, sell_index, position_duration, ratio, buy_signals, sell_signals))
                self.db_connection.commit()
                position_id = self.db_cursor.lastrowid

            return position_id
        except sqlite3.Error as e:
            logger.error(f"An error occurred while saving position: {e}")
            return None

    def get_positions_for_simulation(self, simulation_name, start_ts, end_ts):
        try:
            self.db_cursor.execute('''SELECT DISTINCT p.pair, p.buy_date, p.buy_price, p.sell_date, p.sell_price,
                                               p.buy_index, p.sell_index, p.position_duration, p.ratio,
                                               p.buy_signals, p.sell_signals
                                      FROM positions p
                                      INNER JOIN simulation_positions sp ON p.id = sp.position_id
                                      WHERE sp.simulation_name = ? AND sp.start_ts >= ? AND sp.end_ts <= ?''',
                                   (simulation_name, start_ts, end_ts))
            positions = self.db_cursor.fetchall()
            return positions
        except sqlite3.Error as e:
            logger.error(f"An error occurred while retrieving positions for simulation: {e}")
            return None

    def close(self):
        self.db_connection.close()
