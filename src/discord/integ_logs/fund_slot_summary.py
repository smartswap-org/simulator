import discord
from loguru import logger
from datetime import datetime

async def send_fund_slot_summary_embed(simulator, channel_id, position_id):
    position = simulator.positions.get_position_by_id(position_id)
    if not position:
        logger.error(f"Position not found for ID: {position_id}")
        return

    simulation_name = position['simulation_name']
    fund_slot = position['fund_slot']
    
    ratios = simulator.positions.get_ratios_for_fund_slot(simulation_name, fund_slot)
    
    if not ratios:
        logger.info(f"No ratios found for fund slot {fund_slot}")
        total_profit = 0.0
    else:
        total_profit = 1.0
        for ratio in ratios:
            total_profit *= ratio
        total_profit = round(total_profit, 3)
    
    guild = simulator.discord_bot.get_guild(int(simulator.bot_config.get("discord_id", "")))
    channel = guild.get_channel(int(channel_id))
    if channel is None:
        logger.error(f"Channel not found for ID: {channel_id}")
        return

    embed = discord.Embed(
        title="📉 Fund Slot Summary",
        description=f"Summary for fund slot **{fund_slot}**.",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="🔢 Position ID", value=position['id'], inline=False)
    embed.add_field(name="💵 Currency Pair", value=position['pair'], inline=True)
    embed.add_field(name="📅 Sell Date", value=position['sell_date'], inline=True)
    embed.add_field(name="💲 Sell Price", value=f"${position['sell_price']:.2f}", inline=True)
    embed.add_field(name="📈 Ratios", value=", ".join([f"{r:.3f}" for r in ratios]), inline=False)
    embed.add_field(name="💰 Total Profit", value=f"{total_profit:.3f}", inline=True)

    embed.set_footer(text="SmartSwap Simulator", icon_url="https://github.com/smartswap-org/simulator/blob/main/assets/simulator-logo.jpeg?raw=true")

    async for message in channel.history(limit=10):
        if message.author == simulator.discord_bot.user and message.embeds and message.embeds[0].to_dict() == embed.to_dict():
            return

    await channel.send(embed=embed)