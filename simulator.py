# =============================================================================
# Smartswap Simulator
# =============================================================================
# A module of Smartswap that simulates trading strategies in real-time combined
# with capital management strategies.
#
# Repository: https://github.com/smartswap-org/simulator
# Author: Simon
# =============================================================================
# Description of this file:
# This file is the main file of the simulator, you can run simulator.py using some arguments:
# -debug : this parameter will log the debug logs in the folder 'logs/'

import discord
import socket
import sqlite3
import argparse
import os
from discord.ext import tasks
from discord import Activity, ActivityType
from datetime import datetime
from loguru import logger
from src.discord.configs import get_discord_config

# argument parser for handling debug mode
parser = argparse.ArgumentParser(description='Run the simulator.')
parser.add_argument('-debug', action='store_true', help='Run in debug mode')
args = parser.parse_args()

# directory for log files
log_dir = 'logs'
if not os.path.exists(log_dir):  # create the logs directory if it doesn't exist
    os.makedirs(log_dir)

# log file name based on current date
log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

# configure loguru to handle logging, with DEBUG level if -debug is used
logger.add(log_file, rotation="00:00", retention="7 days", level="DEBUG" if args.debug else "INFO")

class Simulator:
    def __init__(self, discord_bot, bot_config):
        self.discord_bot = discord_bot  # Discord bot instance
        self.bot_config = bot_config  # configuration for the bot, available in configs/discord_bot.json

    #@tasks.loop(seconds=1)
    #async def simulates_loop(self):
    #    """
    #    Loop to run the simulation periodically
    #    """
    #    await simulates(self)  # call the simulates function in a loop

    #async def start_simulation(self):
    #    """
    #    Start the simulation and log the start message to Discord
    #    """
    #    await log(self, self.bot_config["logs_channel_id"], "🚀 Started", 
    #                   f"Simulator has been started on host: {socket.gethostname()}")  
    #    self.simulates_loop.start()  # start the simulation loop

class MyClient(discord.Client):
    async def on_ready(self):
        """
        Event handler for when the bot is ready
        """
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})') 
        #await simulator.start_simulation()  # start the simulation
        await self.change_presence(activity=Activity(type=ActivityType.custom, name=" ", state="🚀 working"))  # set bot presence

discord_bot = MyClient(intents=discord.Intents.all()) # create the Discord bot instance
simulator = Simulator(discord_bot, get_discord_config())  # create the simulator instance
discord_bot.run(simulator.bot_config["token"])  # run the bot with the token from the config
