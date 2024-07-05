import sqlite3
import json

class DatabaseManager:
    def __init__(self, db_path='simulator.db'):
        self.db_connection = sqlite3.connect(db_path)
        self.db_cursor = self.db_connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS simulations (
                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  simulation_name TEXT,
                                  start_ts TEXT,
                                  end_ts TEXT,
                                  positions TEXT)''')
        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS positions (
                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  simulation_id INTEGER,
                                  pair TEXT,
                                  buy_date TEXT,
                                  buy_price REAL,
                                  sell_date TEXT,
                                  sell_price REAL,
                                  FOREIGN KEY(simulation_id) REFERENCES simulations(id))''')
        self.db_connection.commit()

    def save_simulation_data(self, simulation_name, start_ts, end_ts, positions):
        self.db_cursor.execute('''INSERT INTO simulations (simulation_name, start_ts, end_ts, positions) 
                                  VALUES (?, ?, ?, ?)''', 
                               (simulation_name, start_ts, end_ts, json.dumps(positions)))
        self.db_connection.commit()

    def save_position(self, simulation_id, pair, buy_date, buy_price, sell_date, sell_price):
        self.db_cursor.execute('''INSERT INTO positions (simulation_id, pair, buy_date, buy_price, sell_date, sell_price) 
                                  VALUES (?, ?, ?, ?, ?, ?)''', 
                               (simulation_id, pair, buy_date, buy_price, sell_date, sell_price))
        self.db_connection.commit()
