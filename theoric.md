# Smartswap Simulator (Theoric)
Full Theoric of the simulator.

<img src="https://github.com/smartswap-org/simulator/blob/74493bf848cdb234507e7518d06b5dd75421079b/assets/simulator-logo.jpeg" width="250" height="250">

---

### Start Setup

When the simulation starts, it verifies whether the local database "simulator" exists; if not, it creates one. 

Next, it creates a table for each simulation with the following structure:

```sql
CREATE TABLE IF NOT EXISTS simulations (
    simulation_name TEXT,
    start_ts TEXT,
    end_ts TEXT,
    PRIMARY KEY (simulation_name, start_ts, end_ts)
);

CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair TEXT,
    buy_date TEXT,
    buy_price REAL,
    sell_date TEXT,
    sell_price REAL
);

CREATE TABLE IF NOT EXISTS simulation_positions (
    simulation_name TEXT,
    start_ts TEXT,
    end_ts TEXT,
    position_id INTEGER,
    FOREIGN KEY(simulation_name, start_ts, end_ts) REFERENCES simulations(simulation_name, start_ts, end_ts),
    FOREIGN KEY(position_id) REFERENCES positions(id),
    PRIMARY KEY (simulation_name, start_ts, end_ts, position_id)
);
```

Where `start_ts` corresponds to the start of the analysis, and `end_ts` to the day being analyzed. If the simulation is set to run in real-time, `end_ts` will be the current day.

### Simulation Logic

The algorithm starts from the principle that it will analyze from `simulation['api']['start_ts']` to `simulation['api']['end_ts']` as specified in the configuration. However, it does this day by day, extending the search one day at a time.

For example, if `start_ts = 2020-01-01` and `end_ts = 2020-01-05`, the algorithm will proceed as follows:
- 2020-01-01 to 2020-01-02
- 2020-01-01 to 2020-01-03
- 2020-01-01 to 2020-01-04
- 2020-01-01 to 2020-01-05

If a buy position is detected on Solana Crypto during the frame 2020-01-01 to 2020-01-02, it will insert this position into the database: `positions = {"Solana": position_details}`. It will be considered as a current position, so you will have buy_date, buy_price, ... But no any infos about sell date and sell price.

Only buy positions are stored. To detect a sell position, if a specific buy index is present in the frame 2020-01-01 to 2020-01-02 but absent in the subsequent frame 2020-01-01 to 2020-01-03, it is concluded that the position has been sold.

### Logic for Buying in the First Frame

To determine the number of positions, use `simulation['positions']['position_%_invest']`. If it is 20, on a capital of 100 EUR, a maximum of 20 EUR will be invested per position, allowing for 5 positions (100/20).

To determine which positions to take, the algorithm will analyze `simulation['api']['pairs_list']` and scan for buy positions for each pair within the studied timeframe. Once the list of pairs with positions is obtained, the first 5 pairs are selected. Later, a more advanced algorithm might be implemented to choose the 5 pairs based on their history and capitalization.

### Logic for Buying in the Second Frame

Considering that the first frame has already been analyzed and positions have been chosen, the following steps are taken for the current frame:

- If all positions from the first frame are still valid, no new positions are sought.
- If only 4 positions are still valid (one has disappeared), it means a position has been sold. A message is sent to the integrator, and a new position is sought.
