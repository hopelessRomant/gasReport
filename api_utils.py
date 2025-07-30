import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

def safe_api_request(url, key):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except (requests.RequestException, ValueError) as e:
        logging.error(f"[{key}] API error: {e}")
        return None

def get_gas_prices():
    """Fetch gas prices from Etherscan API."""
    if not ETHERSCAN_API_KEY:
        logging.error("ETHERSCAN_API_KEY not found in .env")
        return {"safe": 0, "average": 0, "fast": 0}

    url = f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={ETHERSCAN_API_KEY}"
    result = safe_api_request(url, "get_gas_prices")
    if not result or "result" not in result:
        return {"safe": 0, "average": 0, "fast": 0}

    r = result["result"]
    return {
        "safe": float(r.get("SafeGasPrice", 0)),
        "average": float(r.get("ProposeGasPrice", 0)),
        "fast": float(r.get("FastGasPrice", 0)),
    }

def get_eth_prices(currency="usd"):
    """Fetch ETH price in the requested currency from CoinGecko API."""
    url = f"https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies={currency}"
    result = safe_api_request(url, "get_eth_prices")
    if not result or "ethereum" not in result:
        return {}
    return result["ethereum"]
