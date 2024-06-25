import json

def get_discord_config():
    """
    Function to read bot configuration from bot_config.json
    """
    with open("configs/discord_bot.json", "r") as f:
        return json.load(f)
