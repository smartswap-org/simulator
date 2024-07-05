import sqlite3

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
                                  sell_price REAL)''')
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
            print(f"Simulation data saved successfully: {simulation_name}, {start_ts} to {end_ts}")
        except sqlite3.Error as e:
            print(f"An error occurred while saving simulation data: {e}")

    def save_position(self, simulation_name, start_ts, end_ts, pair, buy_date, buy_price, sell_date, sell_price):
        try:
            # Check if the position already exists
            self.db_cursor.execute('''SELECT id FROM positions WHERE pair = ? AND buy_date = ? AND buy_price = ? AND sell_date = ? AND sell_price = ?''', 
                                   (pair, buy_date, buy_price, sell_date, sell_price))
            position = self.db_cursor.fetchone()
            if position:
                position_id = position[0]
            else:
                self.db_cursor.execute('''INSERT INTO positions (pair, buy_date, buy_price, sell_date, sell_price) 
                                          VALUES (?, ?, ?, ?, ?)''', 
                                       (pair, buy_date, buy_price, sell_date, sell_price))
                self.db_connection.commit()
                position_id = self.db_cursor.lastrowid

            # Insert into simulation_positions
            self.db_cursor.execute('''INSERT OR REPLACE INTO simulation_positions (simulation_name, start_ts, end_ts, position_id) 
                                      VALUES (?, ?, ?, ?)''', 
                                   (simulation_name, start_ts, end_ts, position_id))
            self.db_connection.commit()
            print(f"Position saved successfully: {pair}, {buy_date} to {sell_date}")
        except sqlite3.Error as e:
            print(f"An error occurred while saving position: {e}")

    def close(self):
        self.db_connection.close()
