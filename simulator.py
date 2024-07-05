import discord
import socket
from discord.ext import tasks
from src.discord.configs import get_discord_config, get_simulations_config
from src.discord.embeds import send_embed
from src.db.manager import DatabaseManager  
from discord import Activity, ActivityType
import aiohttp
from datetime import datetime, timedelta

class Simulator:
    def __init__(self, discord_bot, bot_config):
        self.discord_bot = discord_bot
        self.bot_config = bot_config
        self.db_manager = DatabaseManager()

    async def log(self, channel_id, title, log):
        guild = self.discord_bot.get_guild(int(self.bot_config.get("discord_id", "")))
        channel = guild.get_channel(int(channel_id))
        if channel is None:
            return
        highest_role = max(self.discord_bot.guilds[0].get_member(self.discord_bot.user.id).roles, 
                           key=lambda r: r.position if r is not None else 0)
        color = highest_role.color if highest_role else discord.Color.green()
        await send_embed(channel, title, log, color)

    async def send_position_embed(self, channel_id, title, position):
        guild = self.discord_bot.get_guild(int(self.bot_config.get("discord_id", "")))
        channel = guild.get_channel(int(channel_id))
        if channel is None:
            return
        embed = discord.Embed(title=title, color=discord.Color.dark_orange())
        embed.add_field(name="Pair", value=position["pair"], inline=False)
        embed.add_field(name="Buy Date", value=position["buy_date"], inline=True)
        embed.add_field(name="Buy Price", value=position["buy_price"], inline=True)
        embed.add_field(name="Buy Index", value=position["buy_index"], inline=True)
        await channel.send(embed=embed)

    @tasks.loop(seconds=1)
    async def simulates(self):
        async with aiohttp.ClientSession() as session:
            simulates_config = get_simulations_config()
            for simulation in simulates_config:
                simulation_name = simulation
                start_ts = datetime.strptime(simulates_config[simulation]["api"]["start_ts"], "%Y-%m-%d")
                end_ts_config = simulates_config[simulation]["api"]["end_ts"]
                end_ts = datetime.strptime(end_ts_config, "%Y-%m-%d") if end_ts_config else datetime.now()

                current_date = start_ts
                while current_date < end_ts:
                    
                    positions = []  # Empty positions

                    print(start_ts.strftime("%Y-%m-%d"), current_date.strftime("%Y-%m-%d"))

                    # Save simulation data with empty positions, formatting dates as needed
                    self.db_manager.save_simulation_data(simulation_name, start_ts.strftime("%Y-%m-%d"), current_date.strftime("%Y-%m-%d"), positions)

                    # Update current date
                    current_date += timedelta(days=1)
        
    async def start_simulation(self):
        await self.log(self.bot_config["logs_channel_id"], "🚀 Started", 
                       f"Simulator has been started on host: {socket.gethostname()}")
        self.simulates.start()

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        await simulator.start_simulation()
        await self.change_presence(activity=Activity(type=ActivityType.custom, name=" ", state="🚀 working"))

discord_bot = MyClient(intents=discord.Intents.all())
simulator = Simulator(discord_bot, get_discord_config())
discord_bot.run(simulator.bot_config["token"])
