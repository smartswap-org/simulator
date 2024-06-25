import json

def get_config(config):
    """
    Function to read bot configuration from configs/
    """
    with open(config, "r") as f:
        return json.load(f)

def get_discord_config():
    return get_config("configs/discord_bot.json")

def get_simulations_config():
    return get_config("configs/simulations.json")
