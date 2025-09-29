# api_utils.py
import os
import json
import requests
import logging
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_CHAIN_ID = os.getenv("ETHERSCAN_CHAIN_ID", "1")  # default to mainnet


def safe_api_request(url: str, key: str):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        logging.error("[%s] network error: %s", key, e)
        return None

    text = resp.text or ""
    # Prefer JSON parse
    try:
        return resp.json()
    except ValueError:
        # Not valid JSON — wrap raw text so callers get a dict and we keep diagnostics
        txt = text.strip()
        if not txt:
            logging.error("[%s] empty response body", key)
            return None
        logging.warning("[%s] response not JSON; returning wrapped raw text (first 300 chars): %s", key, txt[:300])
        # try to salvage if it *looks* like JSON stored as a string
        try:
            return json.loads(txt)
        except Exception:
            return {"_raw_text": txt}

def get_gas_prices(chain_id: Optional[str] = None):
    """
    Fetch gas prices using Etherscan API v2 (gasoracle). Returns normalized dict of floats:
    {"safe": float, "average": float, "fast": float}
    If anything goes wrong, returns zeros for each entry (safe fallback for the UI).
    """
    if not ETHERSCAN_API_KEY:
        logging.error("ETHERSCAN_API_KEY not found in .env")
        return {"safe": 0.0, "average": 0.0, "fast": 0.0}

    chain_id = chain_id or ETHERSCAN_CHAIN_ID or "1"

    # Etherscan v2 migration: use /v2/api and include chainid param
    url = (
        f"https://api.etherscan.io/v2/api"
        f"?chainid={chain_id}"
        f"&module=gastracker"
        f"&action=gasoracle"
        f"&apikey={ETHERSCAN_API_KEY}"
    )

    result = safe_api_request(url, "get_gas_prices")
    if not result or not isinstance(result, dict):
        logging.error("[get_gas_prices] bad result: %r", result)
        return {"safe": 0.0, "average": 0.0, "fast": 0.0}

    # If upstream returned wrapped raw text, bail and log it
    if "_raw_text" in result:
        logging.error("[get_gas_prices] upstream returned non-JSON: %s", result["_raw_text"][:300])
        return {"safe": 0.0, "average": 0.0, "fast": 0.0}

    # expected shape: {"status":"1","message":"OK","result": { ... } }
    r = result.get("result")
    if isinstance(r, str):
        # Etherscan sometimes returns a human-readable message in 'result'
        logging.error("[get_gas_prices] unexpected 'result' structure (string): %s", r[:300])
        return {"safe": 0.0, "average": 0.0, "fast": 0.0}

    if not isinstance(r, dict):
        logging.error("[get_gas_prices] unexpected 'result' structure: %r", r)
        return {"safe": 0.0, "average": 0.0, "fast": 0.0}

    def safe_float(x):
        try:
            return float(x)
        except Exception:
            try:
                return float(str(x).replace(",", ""))
            except Exception:
                return 0.0

    return {
        "safe": safe_float(r.get("SafeGasPrice", 0)),
        "average": safe_float(r.get("ProposeGasPrice", 0)),
        "fast": safe_float(r.get("FastGasPrice", 0)),
    }


def get_eth_prices(currency="usd"):
    """
    Fetch ETH price from CoinGecko. Return the inner dict for `ethereum` normalized to floats.
    Returns {} on failure.
    """
    url = f"https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies={currency}"
    result = safe_api_request(url, "get_eth_prices")

    if not result or not isinstance(result, dict):
        logging.error("[get_eth_prices] bad result: %r", result)
        return {}

    if "_raw_text" in result:
        logging.error("[get_eth_prices] raw text from upstream: %s", result["_raw_text"][:300])
        return {}

    eth = result.get("ethereum")
    if not isinstance(eth, dict):
        logging.error("[get_eth_prices] missing or unexpected 'ethereum' key: %r", result)
        return {}

    normalized = {}
    for k, v in eth.items():
        try:
            normalized[k] = float(v)
        except Exception:
            try:
                normalized[k] = float(str(v).replace(",", ""))
            except Exception:
                normalized[k] = 0.0

    return normalized
