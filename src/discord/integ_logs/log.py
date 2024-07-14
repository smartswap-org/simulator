# =============================================================================
# Smartswap Simulator
# =============================================================================
# Repository: https://github.com/smartswap-org/simulator
# Author of this code: Simon
# =============================================================================
# Description of this file:
# This file contains the fonctions to log messages on a channel in Discord.
# This is used for admin logs (such as bot connections) or errors.
# =============================================================================

import discord 
from src.discord.embeds import send_embed

async def log(simulator, channel_id, title, log): 
    """
    Log a message in a channel on Discord
    """
    guild = simulator.discord_bot.get_guild(int(simulator.bot_config.get("discord_id", "")))  # get the guild (server)
    channel = guild.get_channel(int(channel_id))  # get the channel by ID
    if channel is None:
        return
    # get the highest role of the bot to set the embed color
    highest_role = max(simulator.discord_bot.guilds[0].get_member(simulator.discord_bot.user.id).roles, 
                       key=lambda r: r.position if r is not None else 0)
    color = highest_role.color if highest_role else discord.Color.green()
    await send_embed(channel, title, log, color)  # send an embed message to the channel