from loguru import logger
import sqlite3

def update_simulation_data(db_manager, simulation_name, start_ts, end_ts):
    """
    Update existing simulation data in the database.
    
    simulation_name: Name of the simulation.
    start_ts: New start timestamp of the simulation.
    end_ts: New end timestamp of the simulation.
    """
    try:
        db_manager.db_cursor.execute('''UPDATE simulations SET start_ts = ?, end_ts = ?
                                  WHERE simulation_name = ?''',
                               (start_ts, end_ts, simulation_name))
        db_manager.db_connection.commit()  # commit the changes
        logger.debug(f"Simulation data updated: {simulation_name}, {start_ts} to {end_ts}")
    except sqlite3.Error as e:
        logger.error(f"An error occurred while updating simulation data: {e}")

def delete_simulation(db_manager, simulation_name, start_ts, end_ts):
    """
    Delete a simulation and all its associated positions from the database.
    
    simulation_name: Name of the simulation.
    start_ts: Start timestamp of the simulation.
    end_ts: End timestamp of the simulation.
    """
    try:
        db_manager.db_cursor.execute('''DELETE FROM simulations WHERE simulation_name = ? AND start_ts = ? AND end_ts = ?''',
                               (simulation_name, start_ts, end_ts))
        db_manager.db_cursor.execute('''DELETE FROM simulation_positions WHERE simulation_name = ? AND start_ts = ? AND end_ts = ?''',
                               (simulation_name, start_ts, end_ts))
        db_manager.db_connection.commit()  # commit the changes
        logger.debug(f"Simulation deleted: {simulation_name}, {start_ts} to {end_ts}")
    except sqlite3.Error as e:
        logger.error(f"An error occurred while deleting simulation: {e}")


def save_simulation_data(db_manager, simulation_name, start_ts, end_ts):
    """
    
    simulation_name: Name of the simulation.
    start_ts: Start timestamp of the simulation.
    end_ts: End timestamp of the simulation.
    """
    try:
        db_manager.db_cursor.execute('''INSERT OR REPLACE INTO simulations (simulation_name, start_ts, end_ts) 
                                  VALUES (?, ?, ?)''', 
                               (simulation_name, start_ts, end_ts))
        db_manager.db_connection.commit()  # commit the changes
        logger.debug(f"Simulation data saved: {simulation_name}, {start_ts} to {end_ts}")
    except sqlite3.Error as e:
        logger.error(f"An error occurred while saving simulation data: {e}")
