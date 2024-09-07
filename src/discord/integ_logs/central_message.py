import discord
from loguru import logger
from datetime import datetime
from src.internal.mng import ensure_internal_ini, read_simulation_data, write_simulation_data

async def send_or_update_central_summary_embed(simulator, channel_id, simulation_name):
    ensure_internal_ini()
    
    central_message_id = read_simulation_data(simulation_name)
    
    positions = simulator.positions.get_positions_by_simulation(simulation_name)
    
    if not positions:
        logger.info(f"No positions found for simulation {simulation_name}")
        return

    fund_slot_data = {}
    for position in positions:
        fund_slot = position[11]  
        #position_id = position[0]  
        buy_date = position[3] if position[3] is not None else "N/A"
        sell_date = position[5] if position[5] is not None else "N/A"
        ratio = position[10] if position[10] is not None else 1.0  

        if fund_slot not in fund_slot_data:
            fund_slot_data[fund_slot] = {
                "last_buy_date": buy_date,
                "last_sell_date": sell_date,
                "last_ratio": ratio,
                "total_profit": 1.0
            }
        
        if sell_date > fund_slot_data[fund_slot]["last_sell_date"]:
            fund_slot_data[fund_slot]["last_sell_date"] = sell_date
        if buy_date > fund_slot_data[fund_slot]["last_buy_date"]:
            fund_slot_data[fund_slot]["last_buy_date"] = buy_date
        fund_slot_data[fund_slot]["last_ratio"] = ratio
        
        ratios = simulator.positions.get_ratios_for_fund_slot(simulation_name, fund_slot)
        if ratios:
            total = 1.0 
            for ratio in ratios:
                total = total * ratio
            fund_slot_data[fund_slot]["total_profit"] = total 
    
    embed = discord.Embed(
        title="📊 **Central Summary**",
        description=f"Summary for all fund slots in simulation **{simulation_name}**.",
        color=discord.Color.pink(), # blue
        timestamp=datetime.utcnow()
    )
    
    for fund_slot, data in fund_slot_data.items():
        last_ratio_str = f'{data["last_ratio"]:.3f}'
        total_profit = round(data["total_profit"], 3)
        last_buy_date_str = data["last_buy_date"]
        last_sell_date_str = data["last_sell_date"]
        
        embed.add_field(
            name=f"**💰 Fund Slot {fund_slot}**",
            value=f"📅 Last Buy Date: {last_buy_date_str}\n"
                  f"📅 Last Sell Date: {last_sell_date_str}\n"
                  f"📈 Last Ratio: {last_ratio_str}\n"
                  f"**🚀 Total Profit:** {total_profit:.3f}\n",
            inline=False  
        )

    guild = simulator.discord_bot.get_guild(int(simulator.bot_config.get("discord_id", "")))
    channel = guild.get_channel(int(channel_id))
    if channel is None:
        logger.error(f"Channel not found for ID: {channel_id}")
        return

    if central_message_id:
        try:
            message = await channel.fetch_message(central_message_id)
            if message.embeds and message.embeds[0].to_dict() == embed.to_dict():
                return  
            await message.edit(embed=embed)
            return
        except discord.NotFound:
            logger.error(f"Message with ID {central_message_id} not found, sending a new message.")
        except discord.HTTPException as e:
            logger.error(f"Failed to fetch or edit message: {e}")
            return

    new_message = await channel.send(embed=embed)
    #existing_central_message_id = read_simulation_data(simulation_name)
    write_simulation_data(simulation_name, new_message.id)

    try:
        await new_message.pin()
        logger.info(f"Message with ID {new_message.id} pinned successfully.")
    except discord.HTTPException as e:
        logger.error(f"Failed to pin message: {e}")