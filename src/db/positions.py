from datetime import datetime

class Positions:
    def __init__(self, db_manager):
        """
        Initialize the Positions manager.
        
        db_manager: An instance of DatabaseManager.
        """
        self.db_manager = db_manager

    def get_positions_by_simulation(self, simulation_name, start_ts=None, end_ts=None):
        """
        Get all positions for a specific simulation_name within an optional timeframe.

        simulation_name: The name of the simulation.
        start_ts: Start timestamp (inclusive) in 'YYYY-MM-DD' format, optional.
        end_ts: End timestamp (inclusive) in 'YYYY-MM-DD' format, optional.

        Returns:
            List of positions matching the criteria.
        """
        query = "SELECT * FROM positions WHERE simulation_name = ?"
        params = [simulation_name]

        if start_ts:
            query += " AND buy_date >= ?"
            params.append(start_ts)
        if end_ts:
            query += " AND buy_date <= ?"
            params.append(end_ts)

        self.db_manager.db_cursor.execute(query, params)
        return self.db_manager.db_cursor.fetchall()

    def get_open_positions(self, simulation_name):
        """
        Get all positions for a specific simulation_name that have no sell_index (i.e., still open).

        simulation_name: The name of the simulation.

        Returns:
            List of open positions.
        """
        query = "SELECT * FROM positions WHERE simulation_name = ? AND sell_index IS NULL"
        self.db_manager.db_cursor.execute(query, [simulation_name])
        return self.db_manager.db_cursor.fetchall()

    def create_position(self, simulation_name, pair, buy_date, buy_price, buy_index, fund_slot, buy_signal):
        """
        Create a new position for a specific simulation_name.

        simulation_name: The name of the simulation.
        pair: The trading pair (e.g., 'BTC/USD').
        buy_date: The buy date in 'YYYY-MM-DD' format.
        buy_price: The price at which the asset was bought.
        buy_index: The index corresponding to the buy signal.
        fund_slot: The portion of the fund allocated to this position.
        buy_signal: Any signals associated with the buy decision.

        Returns:
            The ID of the newly created position.
        """
        buy_price = round(buy_price, 3)
        fund_slot = round(fund_slot, 3)

        query = '''INSERT INTO positions (simulation_name, pair, buy_date, buy_price, buy_index, fund_slot, buy_signal)
                VALUES (?, ?, ?, ?, ?, ?, ?)'''
        self.db_manager.db_cursor.execute(query, 
            (simulation_name, pair, buy_date, buy_price, buy_index, fund_slot, buy_signal))
        self.db_manager.db_connection.commit()
        return self.db_manager.db_cursor.lastrowid

    def get_free_fund_slots(self, simulation_name, pair_name, max_slots):
        """
        Get all free fund slots for a specific pair.

        simulation_name: The name of the simulation.
        pair_name: The trading pair (e.g., 'BTC/USD').
        max_slots: Maximum number of fund slots allowed.

        Returns:
            List of available fund slots.
        """
        used_slots = {pos['fund_slot'] for pos in self.get_open_positions_by_pair(simulation_name, pair_name)}
        return [slot for slot in range(1, max_slots + 1) if slot not in used_slots]

    def close_position(self, position_id, sell_date, sell_price, sell_index, sell_signal):
        """
        Close (sell) an open position by updating it with the sell information.

        position_id: The ID of the position to close.
        sell_date: The sell date in 'YYYY-MM-DD' format.
        sell_price: The price at which the asset was sold.
        sell_index: The index corresponding to the sell signal.
        sell_signal: Any signals associated with the sell decision.

        Returns:
            None
        """
        # Fetch the position to calculate duration and ratio
        self.db_manager.db_cursor.execute("SELECT buy_date, buy_price FROM positions WHERE id = ?", [position_id])
        position = self.db_manager.db_cursor.fetchone()

        if not position:
            raise ValueError(f"No position found with ID {position_id}")

        buy_date_str, buy_price = position
        buy_date = datetime.strptime(buy_date_str, '%Y-%m-%d')
        sell_date_obj = datetime.strptime(sell_date, '%Y-%m-%d')

        # Calculate position duration (in days)
        position_duration = (sell_date_obj - buy_date).days

        # Calculate the profit/loss ratio
        ratio = round(sell_price / buy_price, 3)  # Round ratio to 3 decimal places

        sell_price = round(sell_price, 3)

        # Update the position with the sell information
        query = '''UPDATE positions
                    SET sell_date = ?, sell_price = ?, sell_index = ?, sell_signal = ?, 
                    position_duration = ?, ratio = ?
                WHERE id = ?'''
        self.db_manager.db_cursor.execute(query, 
        (sell_date, sell_price, sell_index, sell_signal, position_duration, ratio, position_id))
        self.db_manager.db_connection.commit()

    def get_most_recent_date(self, simulation_name):
        """
        Get the most recent date (either sell_date or buy_date) for a given simulation_name.

        simulation_name: The name of the simulation.

        Returns:
            The most recent date as a string in 'YYYY-MM-DD' format.
        """
        query = '''
        SELECT MAX(
            CASE 
                WHEN sell_date IS NOT NULL THEN sell_date
                ELSE buy_date
            END
        ) as most_recent_date
        FROM positions
        WHERE simulation_name = ?
        '''
        self.db_manager.db_cursor.execute(query, [simulation_name])
        result = self.db_manager.db_cursor.fetchone()
        return result[0] if result else None
    def get_open_positions_by_pair(self, simulation_name, pair_name):
        """
        Get all open positions for a specific simulation_name and trading pair.

        simulation_name: The name of the simulation.
        pair_name: The trading pair (e.g., 'BTC/USD').

        Returns:
            List of open positions for the specified pair as dictionaries.
        """
        query = '''
        SELECT * FROM positions 
        WHERE simulation_name = ? 
        AND pair = ? 
        AND sell_index IS NULL
        '''
        self.db_manager.db_cursor.execute(query, [simulation_name, pair_name])
        columns = [column[0] for column in self.db_manager.db_cursor.description]
        rows = self.db_manager.db_cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def get_max_index_for_pair(self, simulation_name, pair_name):
        """
        Get the maximum index (either buy_index or sell_index) for a specific pair 
        in a given simulation, considering all current and past positions.

        simulation_name: The name of the simulation.
        pair_name: The trading pair (e.g., 'BTC/USD').

        Returns:
            The maximum index value among all buy_index and sell_index for the specified pair.
            If no positions exist, returns None.
        """
        query = '''
        SELECT MAX(
            CASE 
                WHEN buy_index IS NOT NULL AND sell_index IS NOT NULL THEN 
                    CASE 
                        WHEN buy_index > sell_index THEN buy_index
                        ELSE sell_index 
                    END
                WHEN buy_index IS NOT NULL THEN buy_index
                WHEN sell_index IS NOT NULL THEN sell_index
                ELSE 0
            END
        ) as max_index
        FROM positions 
        WHERE simulation_name = ? 
        AND pair = ?
        '''
        self.db_manager.db_cursor.execute(query, [simulation_name, pair_name])
        result = self.db_manager.db_cursor.fetchone()
        return result[0] if result else None
    def get_position_by_id(self, position_id):
        """
        Retrieve a position by its ID.

        position_id: The ID of the position to retrieve.

        Returns:
            The position as a dictionary if found, otherwise None.
        """
        query = "SELECT * FROM positions WHERE id = ?"
        self.db_manager.db_cursor.execute(query, [position_id])
        row = self.db_manager.db_cursor.fetchone()
        
        if row:
            columns = [column[0] for column in self.db_manager.db_cursor.description]
            return dict(zip(columns, row))
        return None