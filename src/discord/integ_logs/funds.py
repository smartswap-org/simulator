# =============================================================================
# Smartswap Simulator
# =============================================================================
# Repository: https://github.com/smartswap-org/simulator
# Author of this code: Simon
# =============================================================================
# Description of this file:
# This file contains all the fonctions thats are used to logs in Discord the
# current funds slots and benefits.
# =============================================================================

import discord
from datetime import datetime
import json

async def send_funds_embed(simulator, channel_id, start_ts, end_ts, last_fund_entry, new_funds):
    guild = simulator.discord_bot.get_guild(int(simulator.bot_config.get("discord_id", "")))  # get the guild (server)
    channel = guild.get_channel(int(channel_id))  # get the channel by ID
    if channel is None:
        return

    if isinstance(end_ts, str):
        end_ts_datetime = datetime.strptime(end_ts, "%Y-%m-%d")
    else:
        end_ts_datetime = end_ts

    title_line = f"<:tetherusdt:1262038840584044624> Funds"
    
    description_lines = []
    description_lines.append(json.dumps(last_fund_entry))
    description_lines.append(json.dumps(new_funds))

    embed = discord.Embed(
        title=title_line,
        description="\n".join(description_lines),
        color=0xACBFA4
    )

    #embed.set_author(name="Smartswap", icon_url="https://avatars.githubusercontent.com/u/171923264?s=200&v=4")
    embed.set_footer(text=f"Simulation from {start_ts} to {end_ts}")

    # Check for duplicate messages in the last 10 messages
    async for message in channel.history(limit=10):
        if message.author == simulator.discord_bot.user and message.embeds:
            if message.embeds[0].description == embed.description and message.embeds[0].footer.text == embed.footer.text:
                return  # Do not send the message if it's the same as the last one

    await channel.send(embed=embed)