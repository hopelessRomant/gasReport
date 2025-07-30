from api_utils import get_gas_prices, get_eth_prices

def get_gas_costs_json(gas_used, currency="usd"):
    gas_prices = get_gas_prices()
    eth_price_data = get_eth_prices(currency)

    if not eth_price_data:
        return {"error": "Failed to fetch ETH price"}

    eth_price_cur = eth_price_data.get(currency, 0)
    eth_price_usd = eth_price_data.get("usd", 0)

    results = []
    for speed, gwei in gas_prices.items():
        gas_cost_eth = gas_used * gwei * 1e-9
        gas_cost_usd = gas_cost_eth * eth_price_usd
        gas_cost_cur = gas_cost_eth * eth_price_cur

        results.append({
            "speed": speed,
            "eth_cost": gas_cost_eth,
            "usd_cost": gas_cost_usd,
            "currency_cost": gas_cost_cur
        })

    return {"gas_costs": results, "current_gas_prices_gwei": gas_prices}
