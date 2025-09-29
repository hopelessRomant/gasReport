import logging
from api_utils import get_gas_prices, get_eth_prices

def _safe_float(val, default=0.0):
    try:
        return float(val)
    except Exception:
        try:
            return float(str(val).replace(",", ""))
        except Exception:
            return default


def get_gas_costs_json(gas_used, currency="usd"):
    """
    Return a dict with:
        {"gas_costs": [...], "current_gas_prices_gwei": {...}}
    Or return {"error": "..."} on fatal problems.
    This function is defensive: it never returns a bare string.
    """
    # ensure gas_used is numeric
    try:
        gas_used_val = _safe_float(gas_used, default=0.0)
    except Exception:
        gas_used_val = None

    if gas_used_val is None:
        return {"error": "Invalid gas_used value"}

    currency = (currency or "usd").lower()

    gas_prices = get_gas_prices()
    if not isinstance(gas_prices, dict) or not gas_prices:
        logging.error("Failed to get gas prices or unexpected format: %r", gas_prices)
        # fallback to zeros instead of blowing up
        gas_prices = {"safe": 0.0, "average": 0.0, "fast": 0.0}

    eth_price_data = get_eth_prices(currency)
    if not isinstance(eth_price_data, dict) or not eth_price_data:
        # If we couldn't fetch prices, return an error dict (GUI expects dicts)
        return {"error": "Failed to fetch ETH price"}

    eth_price_cur = _safe_float(eth_price_data.get(currency, 0))
    eth_price_usd = _safe_float(eth_price_data.get("usd", eth_price_cur if currency == "usd" else 0))

    results = []
    for speed, gwei in list(gas_prices.items()):
        gwei_val = _safe_float(gwei)
        gas_cost_eth = gas_used_val * gwei_val * 1e-9
        gas_cost_usd = gas_cost_eth * eth_price_usd
        gas_cost_cur = gas_cost_eth * eth_price_cur

        results.append({
            "speed": speed,
            "eth_cost": gas_cost_eth,
            "usd_cost": gas_cost_usd,
            "currency_cost": gas_cost_cur
        })

    return {
        "gas_costs": results,
        "current_gas_prices_gwei": {k: _safe_float(v) for k, v in gas_prices.items()}
    }
