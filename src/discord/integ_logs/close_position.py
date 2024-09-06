# =============================================================================
# Smartswap Simulator
# =============================================================================
# Repository: https://github.com/smartswap-org/simulator
# Author of this code: Simon
# =============================================================================
# Description of this file:
# This file contains all the fonctions thats are used to logs in Discord the
# current positions of a ts interval.
# =============================================================================

import discord
from datetime import datetime
from loguru import logger 

async def send_close_position_embed(simulator, channel_id, position_id):
    position = simulator.positions.get_position_by_id(position_id)

    guild = simulator.discord_bot.get_guild(int(simulator.bot_config.get("discord_id", "")))
    channel = guild.get_channel(int(channel_id))
    if channel is None:
        logger.error(f"Channel not found for ID: {channel_id}")
        return

    embed = discord.Embed(
        title="💼 Position Closed!",
        description=f"The position for **{position['pair']}** has been closed.",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="🔢 Position ID", value=position['id'], inline=False)
    embed.add_field(name="💵 Currency Pair", value=position['pair'], inline=True)
    embed.add_field(name="📅 Buy Date", value=position['buy_date'], inline=True)
    embed.add_field(name="💲 Buy Price", value=f"${position['buy_price']:.2f}", inline=True)
    embed.add_field(name="📅 Sell Date", value=position['sell_date'], inline=True)
    embed.add_field(name="💲 Sell Price", value=f"${position['sell_price']:.2f}", inline=True)
    embed.add_field(name="📉 Sell Signal", value=f"{position['sell_signal']}", inline=True)
    embed.add_field(name="⏳ Duration", value=f"{position['position_duration']} days", inline=True)
    embed.add_field(name="📊 Ratio", value=f"{position['ratio']:.3f}", inline=True)

    embed.set_footer(text="SmartSwap Simulator", icon_url="https://github.com/smartswap-org/simulator/blob/main/assets/simulator-logo.jpeg?raw=true")

    async for message in channel.history(limit=10):
        if message.author == simulator.discord_bot.user and message.embeds and message.embeds[0].to_dict() == embed.to_dict():
            return

    await channel.send(embed=embed)