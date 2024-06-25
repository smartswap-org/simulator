import discord
import socket
from discord import Activity, ActivityType
from discord_bot.configs import get_discord_config
from discord_bot.embeds import send_embed

class Simulator(object):
    def __init__(self, discord_bot, bot_config):
        self.discord_bot = discord_bot
        self.bot_config = bot_config
    
    async def log(self, title, log):
        guild = self.discord_bot.get_guild(int(self.bot_config.get("discord_id", "")))
        if "logs_channel_id" not in self.bot_config:
            return
        channel = guild.get_channel(int(self.bot_config["logs_channel_id"]))
        if channel is None:
            return
        highest_role = max(self.discord_bot.guilds[0].get_member(self.discord_bot.user.id).roles, 
                           key=lambda r: r.position if r is not None else 0)
        color = highest_role.color if highest_role else discord.Color.green()
        await send_embed(channel, title, log, color)

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        await simulator.log("🚀 Started", f"Simulator has been started on host: {socket.gethostname()}")
        await self.change_presence(activity=Activity(type=ActivityType.custom, name=" ", state="🚀 working"))

discord_bot = MyClient(intents=discord.Intents.all())
simulator = Simulator(discord_bot, get_discord_config())
discord_bot.run(simulator.bot_config["token"])
