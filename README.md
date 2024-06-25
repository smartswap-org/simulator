# simulator
Simulates a trading strategy combined with a portfolio management strategy.

<img src="https://github.com/smartswap-org/simulator/blob/74493bf848cdb234507e7518d06b5dd75421079b/assets/simulator-logo.jpeg" width="250" height="250">

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

## simulates.json
Example of a simulation configuration:
```json
{
    "default-sp_v1": {
        "discord": {
            "discord_channel_id": "1255167159051489280"
        },
        "api": {
            "pairs_list": [
                "BTC/USDT", "ETH/USDT", "BNB/USDT",
                "ADA/USDT", "XRP/USDT", "DOGE/USDT",
                "LTC/USDT", "DOT/USDT", "UNI/USDT",
                "LINK/USDT", "BCH/USDT", "LUNA/USDT",
                "SOL/USDT", "AVAX/USDT", "ALGO/USDT",
                "VET/USDT", "FIL/USDT", "ICP/USDT",
                "MATIC/USDT", "ATOM/USDT", "XLM/USDT",
                "TRX/USDT", "ETC/USDT", "FTT/USDT",
                "THETA/USDT", "XTZ/USDT", "EOS/USDT",
                "AAVE/USDT", "KSM/USDT", "NEO/USDT",
                "MKR/USDT", "CAKE/USDT", "COMP/USDT",
                "ENJ/USDT", "ZEC/USDT", "DASH/USDT",
                "MANA/USDT", "ZIL/USDT", "CHZ/USDT",
                "SAND/USDT", "AXS/USDT"
            ],
            "strategy": "default",
            "start_ts": "",
            "end_ts": "",
            "multi_positions": true
        },
        "positions": {
            "reinvest_gains": false,
            "position_%_invest": 20
        },
        "wallet": {
            "invest_capital": 1000,
            "adjust_invest_capital_if_loss": false
        }
    }
}
```
