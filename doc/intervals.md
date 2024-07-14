# Intervals

Throughout the code, we refer to intervals, which we will call simulations in the database. Intervals are time spans consisting of a start and an end: `start_ts` and `end_ts`. The `start_ts` value is retrieved from the `simulations.json` file, but the `end_ts` value is dynamic and progresses over time.

Currently, the simulator is compatible only with daily simulations, meaning it only moves from day to day. Here, the `end_ts` value dynamically advances by one day (+1 day) at a time.

Each interval is entered for each simulation in the `simulations` table. Finally, positions are assigned to the different simulations (intervals) via the `simulations_positions` table.

For understanding the database structure, refer to: [Database Tables](https://github.com/smartswap-org/simulator/blob/main/src/db/tables.py)

For understanding how simulations are recorded, refer to: [Simulation Recording](https://github.com/smartswap-org/simulator/blob/main/src/db/simulation.py)

For more information on the configuration of `simulations.json` to understand the interval setup, refer to: [Configurations README](https://github.com/smartswap-org/simulator/blob/main/configs/README.md)