# Smartswap Simulator

A module of Smartswap that simulates trading strategies in real-time combined with capital management strategies.

<img src="https://github.com/smartswap-org/simulator/blob/74493bf848cdb234507e7518d06b5dd75421079b/assets/simulator-logo.jpeg" width="250" height="250">

---

### Features:

- **Trading Strategy Simulation**: Test various trading strategies in a simulated environment before applying them to real markets.
- **Capital Management**: Apply capital management strategies in real-time alongside trading strategies from the QTSBE API.
- **Integration**: Includes integration with Discord for real-time notifications and logging.

### Purpose:

The Smartswap Simulator represents the next step after backtesting, allowing you to validate strategies live in the market environment. It also facilitates the application of capital management strategies to trading bots.

### Getting Started:

To begin using the Smartswap Simulator, follow these steps:

1. **Clone the Repository**: `git clone https://github.com/smartswap-org/simulator`
2. **Install Requirements**: `pip install -r requirements.txt`
3. **Configure Discord Settings**: Refer to `configs/README.MD` for instructions on creating `configs/discord_bot.json`.
4. **Configure Simulations**: Refer to `configs/README.MD` for instructions on creating `configs/simulations.json`.
5. **Run the Simulator**: `python simulator.py`

---

### Support and Contribution:

For any issues, suggestions, or contributions, please feel free to open an issue or pull request on [GitHub](https://github.com/smartswap-org/simulator).

---
