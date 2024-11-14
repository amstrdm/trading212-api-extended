# Rest API client for Trading212

Based on the API of [Trading212](https://www.trading212.com/). This Package replaces trading212-rest which is missing most recent endpoints. At the Moment this package contains all endpoints provided by the official [Trading212 API](https://t212public-api-docs.redoc.ly/). Should there be any endpojnts that aren't currently provided feel free to create an issue and I'll implement them ASAP.  

**Recently added Endpoints include:**
- All Pies Endpoints
- History Export Endpoints

## Installation

```bash
pip install trading212-api-extended
```

## Usage

```python
from trading212_api_extended import Trading212

client = Trading212(api_key="your_api_token", demo=False)

orders = client.orders()

dividends = client.dividends()
```

This is just a small selection of functions. Most endpoints are already implemented.

For a full documentation on Trading212 endpoint paramaters see https://t212public-api-docs.redoc.ly/