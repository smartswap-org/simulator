import sqlite3
import json

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
                                  positions TEXT,
                                  PRIMARY KEY (simulation_name, start_ts, end_ts))''')
        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS positions (
                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  simulation_name TEXT,
                                  start_ts TEXT,
                                  end_ts TEXT,
                                  pair TEXT,
                                  buy_date TEXT,
                                  buy_price REAL,
                                  sell_date TEXT,
                                  sell_price REAL,
                                  FOREIGN KEY(simulation_name, start_ts, end_ts) REFERENCES simulations(simulation_name, start_ts, end_ts))''')
        self.db_connection.commit()

    def save_simulation_data(self, simulation_name, start_ts, end_ts, positions):
        try:
            self.db_cursor.execute('''INSERT OR REPLACE INTO simulations (simulation_name, start_ts, end_ts, positions) 
                                      VALUES (?, ?, ?, ?)''', 
                                   (simulation_name, start_ts, end_ts, json.dumps(positions)))
            self.db_connection.commit()
            print(f"Data saved successfully: {simulation_name}, {start_ts} to {end_ts}")
        except sqlite3.Error as e:
            print(f"An error occurred while saving simulation data: {e}")

    def save_position(self, simulation_name, start_ts, end_ts, pair, buy_date, buy_price, sell_date, sell_price):
        self.db_cursor.execute('''INSERT INTO positions (simulation_name, start_ts, end_ts, pair, buy_date, buy_price, sell_date, sell_price) 
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                               (simulation_name, start_ts, end_ts, pair, buy_date, buy_price, sell_date, sell_price))
        self.db_connection.commit()
