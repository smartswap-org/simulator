import configparser
import os

def ensure_internal_ini():
    ini_path = 'ini/internal.ini'
    if not os.path.exists(ini_path):
        config = configparser.ConfigParser()
        config.read_dict({})
        with open(ini_path, 'w') as configfile:
            config.write(configfile)

def read_simulation_data(simulation_name):
    ini_path = 'ini/internal.ini'
    config = configparser.ConfigParser()
    config.read(ini_path)
    central_message_id = config.getint(simulation_name, 'central_message_id', fallback=0)
    return central_message_id

def write_simulation_data(simulation_name, central_message_id):
    ini_path = 'ini/internal.ini'
    config = configparser.ConfigParser()
    config.read(ini_path)
    if not config.has_section(simulation_name):
        config.add_section(simulation_name)
    config.set(simulation_name, 'central_message_id', str(central_message_id))
    with open(ini_path, 'w') as configfile:
        config.write(configfile)