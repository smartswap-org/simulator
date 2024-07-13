# Configs

## configs/discord_bot.json

```json
{
    "token": "your_token_here",
    "prefix": ".",
    "discord_id": "your_discord_id_here",
    "logs_channel_id": "your_logs_channel_id_here"
}
```
1. **Token**: Obtain your bot token from [Discord Developer Portal](https://discord.com/developers/applications/).
2. **Discord ID and Logs Channel ID**:
   - Activate Discord as a developer app.
   - Right-click on your server to get its ID.
   - Right-click on the log channel you created to obtain its ID.
Replace `"your_token_here"`, `"your_discord_id_here"`, and `"your_logs_channel_id_here"` with your actual bot token, Discord server ID, and log channel ID respectively.

## simulations.json
Example of a simulation configuration:
```json
{
    "rsi_example-sp_v1":
    {
        "discord":
            {
                "discord_channel_id": "discord_channel_id_for_this_simulation"
            },
        "api":
            {
                "pairs_list": [
                    "Binance_BTCUSDT_1d",
                    "Binance_ETHUSDT_1d"
                ],
                "strategy": "rsi_example",
                "start_ts": "",
                "end_ts": "",
                "multi_positions": "True"
            },
        "positions":
            {
                "reinvest_gains": "True",
                "position_%_invest": "20"
            },
        "wallet":
            {
                "invest_capital": "1000",
                "adjust_invest_capital_if_loss": "False"
            }
    }
}
```
Notes:
Notes:
- `position_%_invest`: This parameter defines a division. For example, if you specify 20%, it corresponds to 100/20, allowing a maximum of 5 positions simultaneously. If you set `position_%_invest` to -1, it indicates no limit on the number of positions. You must set a number such that 100/`position_%_invest` provides a real number for funds table creation. See `src/db/manager.py`, method `create_funds_table` of the `DatabaseManager` class.