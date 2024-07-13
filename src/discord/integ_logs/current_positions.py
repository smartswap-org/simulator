from datetime import datetime
import discord

async def send_current_positions_embed(simulator, channel_id, start_ts, end_ts, positions):
    guild = simulator.discord_bot.get_guild(int(simulator.bot_config.get("discord_id", "")))  # get the guild (server)
    channel = guild.get_channel(int(channel_id))  # get the channel by ID
    if channel is None:
        return

    if isinstance(end_ts, str):
        end_ts_datetime = datetime.strptime(end_ts, "%Y-%m-%d")
    else:
        end_ts_datetime = end_ts

    title_line = f"⌛ Current Positions"
    
    description_lines = []
    description_lines.append('pair | buy_date | buy_price | duration')
    #description_lines.append('')
    for position in positions:
        buy_date_datetime = datetime.strptime(position['buy_date'], "%Y-%m-%d")
        duration = end_ts_datetime - buy_date_datetime
        line = f"{position['pair']} | {position['buy_date']} | {position['buy_price']} | {duration.days} days"
        description_lines.append(line)
    
    embed = discord.Embed(
        title=title_line,
        description="\n".join(description_lines),
        color=discord.Color.blue()
    )

    #embed.set_author(name="Smartswap", icon_url="https://avatars.githubusercontent.com/u/171923264?s=200&v=4")
    embed.set_footer(text=f"Simulation from {start_ts} to {end_ts}")

    # Check for duplicate messages in the last 10 messages
    async for message in channel.history(limit=10):
        if message.author == simulator.discord_bot.user and message.embeds:
            if message.embeds[0].description == embed.description and message.embeds[0].footer.text == embed.footer.text:
                return  # Do not send the message if it's the same as the last one

    await channel.send(embed=embed)