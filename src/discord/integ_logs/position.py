# =============================================================================
# Smartswap Simulator
# =============================================================================
# Repository: https://github.com/smartswap-org/simulator
# Author of this code: Simon
# =============================================================================
# Description of this file:
# This file contains the fonctions thats are used to logs in Discord the
# open or close positions.
# =============================================================================

import discord 

async def send_position_embed(simulator, channel_id, title, color, position):
    """
    Send a detailed embed message about a position in a channel on Discord.
    Avoid sending duplicate messages by checking the last message in the channel.
    """
    guild = simulator.discord_bot.get_guild(int(simulator.bot_config.get("discord_id", "")))  # get the guild (server)
    channel = guild.get_channel(int(channel_id))  # get the channel by ID
    if channel is None:
        return
    embed = discord.Embed(title=title, color=color)  # create an embed message
    for key in position.keys():
        embed.add_field(name=key, value=position[key], inline=True)
    # retrieve the last message sent by the bot in the channel
    async for message in channel.history(limit=10):  
        if message.author == simulator.discord_bot.user:  # check if the message is from the bot
            # compare the content of the last embed message with the current embed
            if message.embeds and message.embeds[0].to_dict() == embed.to_dict():
                return  # do not send the message if it's the same as the last one
    await channel.send(embed=embed)  # send the embed message to the channel