import discord
import socket
from discord import Activity, ActivityType
from discord.ext import tasks
from discord_bot.configs import get_discord_config, get_simulations_config
from discord_bot.embeds import send_embed
import requests

class Simulator(object):
    def __init__(self, discord_bot, bot_config):
        self.discord_bot = discord_bot
        self.bot_config = bot_config    
    async def log(self, channel_id, title, log):
        guild = self.discord_bot.get_guild(int(self.bot_config.get("discord_id", "")))
        channel = guild.get_channel(int(channel_id))
        if channel is None:
            return
        highest_role = max(self.discord_bot.guilds[0].get_member(self.discord_bot.user.id).roles, 
                           key=lambda r: r.position if r is not None else 0)
        color = highest_role.color if highest_role else discord.Color.green()
        await send_embed(channel, title, log, color)

    @tasks.loop(seconds=1)
    async def simulates(self):
        simulates_config = get_simulations_config()
        for simulation in simulates_config:
            for pairs in simulates_config[simulation]["api"]["pairs_list"]:
                url = f"http://127.0.0.1:5000/QTSBE/{pairs}/{simulates_config[simulation]["api"]["strategy"]}"
                response = requests.get(url)
                response.raise_for_status()

        #await self.log(""", 
        #                "🚀 test", 
        #                 get_simulates_config())

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        await simulator.log(simulator.bot_config["logs_channel_id"], 
                            "🚀 Started", 
                            f"Simulator has been started on host: {socket.gethostname()}")
        await self.change_presence(activity=Activity(type=ActivityType.custom, name=" ", state="🚀 working"))
        simulator.simulates.start()

discord_bot = MyClient(intents=discord.Intents.all())
simulator = Simulator(discord_bot, get_discord_config())
discord_bot.run(simulator.bot_config["token"])
