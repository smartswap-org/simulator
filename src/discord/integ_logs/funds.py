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

    title_line = f"<:tetherusdt:1262038840584044624> Funds"
    
    description_lines = []

    embed = discord.Embed(
        title=title_line,
        description="\n".join(description_lines),
        color=0xACBFA4
    )
    for key in new_funds.keys():
        if key in ['start_ts', 'end_ts']:
            embed.add_field(name=key, value=new_funds[key], inline=True)
        else:
            diff = round(float(new_funds[key])-float(last_fund_entry[key]), 2) 
            if diff != 0.0: 
                if diff > 0:
                    embed.add_field(name=key, value=f"{last_fund_entry[key]} :arrow_right: {new_funds[key]} (:heavy_plus_sign: {diff})", inline=True)
                else:
                    embed.add_field(name=key, value=f"{last_fund_entry[key]} :arrow_right: {new_funds[key]} ({diff})", inline=True)
            else:
                embed.add_field(name=key, value=new_funds[key], inline=True)

    embed.set_footer(text=f"Simulation from {start_ts} to {end_ts}")

    # Check for duplicate messages in the last 10 messages
    async for message in channel.history(limit=10):
        if message.author == simulator.discord_bot.user and message.embeds:
            if message.embeds[0].description == embed.description and message.embeds[0].footer.text == embed.footer.text:
                return  # Do not send the message if it's the same as the last one

    await channel.send(embed=embed)