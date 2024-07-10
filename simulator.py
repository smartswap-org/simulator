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
from discord.ext import tasks
from src.discord.configs import get_discord_config
from src.discord.embeds import send_embed
from src.db.manager import DatabaseManager
from discord import Activity, ActivityType
from datetime import datetime
from loguru import logger
import sqlite3
from src.simulation.simulates import simulates 
import argparse
import os

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
        self.db_manager = DatabaseManager()  # SQLite3 manager (creates tables, database, etc.)

    async def log(self, channel_id, title, log): 
        """
        Log a message in a channel on Discord
        """
        guild = self.discord_bot.get_guild(int(self.bot_config.get("discord_id", "")))  # get the guild (server)
        channel = guild.get_channel(int(channel_id))  # get the channel by ID
        if channel is None:
            return
        # get the highest role of the bot to set the embed color
        highest_role = max(self.discord_bot.guilds[0].get_member(self.discord_bot.user.id).roles, 
                           key=lambda r: r.position if r is not None else 0)
        color = highest_role.color if highest_role else discord.Color.green()
        await send_embed(channel, title, log, color)  # send an embed message to the channel

    async def send_position_embed(self, channel_id, title, color, position):
        """
        Send a detailed embed message about a position in a channel on Discord
        """
        guild = self.discord_bot.get_guild(int(self.bot_config.get("discord_id", "")))  # get the guild (server)
        channel = guild.get_channel(int(channel_id))  # get the channel by ID
        if channel is None:
            return
        embed = discord.Embed(title=title, color=color)  # create an embed message
        # add fields to the embed message
        for key in position.keys():
            embed.add_field(name=key, value=position[key], inline=False)
        await channel.send(embed=embed)  # send the embed message to the channel

    def update_position_sell_info(self, simulation_name, start_ts, end_ts, sell_date, sell_price):
        """
        Update the sell information for a position in the database
        """
        try:
            # update the simulation position in the database
            self.db_manager.db_cursor.execute('''UPDATE simulation_positions SET sell_date = ?, sell_price = ? 
                                      WHERE simulation_name = ? AND start_ts = ? AND end_ts = ?''', 
                                   (sell_date, sell_price, simulation_name, start_ts, end_ts))
            self.db_manager.db_connection.commit()  # Ccmmit the changes to the database
            logger.debug(f"Position updated successfully: {simulation_name}, {start_ts} to {end_ts}")  # log success
        except sqlite3.Error as e:
            logger.error(f"An error occurred while updating position: {e}")  # log error if any

    @tasks.loop(seconds=1)
    async def simulates_loop(self):
        """
        Loop to run the simulation periodically
        """
        await simulates(self)  # call the simulates function in a loop

    async def start_simulation(self):
        """
        Start the simulation and log the start message to Discord
        """
        await self.log(self.bot_config["logs_channel_id"], "🚀 Started", 
                       f"Simulator has been started on host: {socket.gethostname()}")  
        self.simulates_loop.start()  # start the simulation loop

class MyClient(discord.Client):
    async def on_ready(self):
        """
        Event handler for when the bot is ready
        """
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})') 
        await simulator.start_simulation()  # start the simulation
        await self.change_presence(activity=Activity(type=ActivityType.custom, name=" ", state="🚀 working"))  # set bot presence

discord_bot = MyClient(intents=discord.Intents.all()) # create the Discord bot instance
simulator = Simulator(discord_bot, get_discord_config())  # create the simulator instance
discord_bot.run(simulator.bot_config["token"])  # run the bot with the token from the config
