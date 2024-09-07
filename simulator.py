import discord
import socket
#import sqlite3
import argparse
import os
from discord.ext import tasks
from discord import Activity, ActivityType
from datetime import datetime
from loguru import logger
from src.discord.configs import get_discord_config
from src.db.manager import DatabaseManager 
from src.simulation.simulates import simulates
from src.discord.integ_logs.log import log 
from src.db.positions import Positions

# argument parser for handling debug mode
parser = argparse.ArgumentParser(description='Run the simulator.')
parser.add_argument('-debug', action='store_true', help='Run in debug mode')
args = parser.parse_args()

# directory for log files
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)  # create the logs directory if it doesn't exist

# log file name based on current date
log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

# configure loguru to handle logging
logger.add(log_file, rotation="00:00", retention="7 days", level="DEBUG" if args.debug else "INFO")

class Simulator:
    def __init__(self, discord_bot, bot_config, db_path='simulator.db'):
        self.discord_bot = discord_bot
        self.bot_config = bot_config
        self.db_manager = DatabaseManager(db_path)
        self.positions = Positions(self.db_manager)

    def close(self):
        self.db_manager.close()

    @tasks.loop(seconds=1)
    async def simulates_loop(self):
        await simulates(self)

    async def start_simulation(self):
        await log(self, self.bot_config["logs_channel_id"], "🚀 Started", 
                  f"Simulator has been started on host: {socket.gethostname()}")
        self.simulates_loop.start()

class MyClient(discord.Client):
    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        await simulator.start_simulation()
        await self.change_presence(activity=Activity(type=ActivityType.custom, name=" ", state="🚀 working"))

discord_bot = MyClient(intents=discord.Intents.all())
simulator = Simulator(discord_bot, get_discord_config())
try:
    discord_bot.run(simulator.bot_config["token"])
finally:
    simulator.close()