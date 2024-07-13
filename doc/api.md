# QTSBE API Usage for Smartswap Simulator

QTSBE API is used to fetch old and current positions for different trading pairs, along with their respective timestamp intervals.

### Purpose

The purpose of using the API in the Smartswap Simulator is to dynamically retrieve trading positions over specified time intervals. This allows the simulator to:
- Access historical positions for analysis.
- Obtain current positions to simulate real-time scenarios.

### API Endpoint

The simulator interacts with the API endpoint to fetch data. The endpoint URL format is:

http://127.0.0.1:5000/QTSBE/{pair}/{strategy}?start_ts={start_ts}&end_ts={end_ts}&multi_positions={multi_positions}

#### Parameters used
- `pair`: The trading pair for which positions are fetched.
- `strategy`: The trading strategy applied.
- `start_ts`: The start timestamp for the API query.
- `end_ts`: The end timestamp for the API query.
- `multi_positions`: A flag indicating if multiple positions should be fetched.
