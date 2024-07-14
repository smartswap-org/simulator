# =============================================================================
# Smartswap Simulator
# =============================================================================
# Repository: https://github.com/smartswap-org/simulator
# Author of this code: Simon
# =============================================================================
# Description of this file:
# This file contains the fonctions to get configs from folder configs/
# =============================================================================

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
