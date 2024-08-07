# =============================================================================
# Smartswap Simulator
# =============================================================================
# Repository: https://github.com/smartswap-org/simulator
# Author of this code: Simon
# =============================================================================
# Description of this file:
# This file all the fonctions to interract with Discord Embeds.
# =============================================================================

import discord
import time
from datetime import datetime

bot_start_time = time.time()

def create_embed(title, description, color):
    """
    This function creates an embed with 
    title, description, and color 
    for Discord.
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    return embed

def format_time(seconds):
    """
    This function converts a given duration in seconds 
    into a formatted string representing hours, minutes, and seconds.

    Example: format_time(3665) will return "1h 1m 5s"
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

async def send_embed(channel, title, description, color):
    """
    This function creates an embed using the function create_embed,
    gets the time since the bot was started using the global variable bot_start_time,
    and sets this Bot uptime in the footer.
    Then it sends this embed either to a channel or as a reply to a message.
    """
    # truncate title if it's too long
    if len(title) > 256:
        title = title[:253] + "..."  # keep it within 256 characters including "..."
    
    embed = create_embed(title, description, color)
    uptime_seconds = int(time.time() - bot_start_time)
    uptime_str = format_time(uptime_seconds)
    date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    embed.set_footer(text=f"Bot uptime: {uptime_str}, date: {date}")
    await channel.send(embed=embed)

async def error(channel, error):
    """
    Sends an error embed in a channel.
    """
    return await send_embed(channel, "❌ Error", error, discord.Color.brand_red())
