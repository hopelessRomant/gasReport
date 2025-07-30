import logging
from tabulate import tabulate
from api_utils import get_gas_prices, get_eth_prices
from calc_utils import calculate_gas_cost

logging.basicConfig(level=logging.INFO)

def get_gas_costs_json(gas_used, currency="usd"):
    """Fetch gas prices and ETH prices, then return JSON-like dict."""
    gas_prices = get_gas_prices()
    eth_prices = get_eth_prices(currency)

    if not eth_prices or currency not in eth_prices:
        return {"error": f"Failed to fetch ETH price for '{currency.upper()}'"}

    eth_price_usd = get_eth_prices("usd").get("usd", 0)  # Always fetch USD for comparison
    eth_price_target = eth_prices.get(currency, 0)

    results = {
        "currency": currency.upper(),
        "gas_costs": [],
        "current_gas_prices_gwei": gas_prices,
    }

    for speed, gwei in gas_prices.items():
        if gwei == 0 or eth_price_usd == 0 or eth_price_target == 0:
            results["gas_costs"].append({
                "speed": speed,
                "eth_cost": None,
                "usd_cost": None,
                "currency_cost": None,
                "error": "API Error"
            })
            continue

        gas_eth, gas_usd = calculate_gas_cost(gas_used, gwei, eth_price_usd)
        _, gas_cur = calculate_gas_cost(gas_used, gwei, eth_price_target)

        results["gas_costs"].append({
            "speed": speed,
            "eth_cost": round(gas_eth, 8),
            "usd_cost": round(gas_usd, 2),
            "currency_cost": round(gas_cur, 2),
        })

    return results


def main():
    try:
        gas_used = float(input("Enter gas used (e.g. 21000): "))
        if gas_used <= 0:
            raise ValueError
    except ValueError:
        logging.error("Invalid gas input. Please enter a positive number.")
        return

    currency = input("Enter target currency (default USD): ").strip().lower() or "usd"
    results = get_gas_costs_json(gas_used, currency)

    if "error" in results:
        logging.error(results["error"])
        return

    table = []
    for entry in results["gas_costs"]:
        if entry.get("error"):
            table.append([entry["speed"].capitalize(), "API Error", "-", "-"])
        else:
            table.append([
                entry["speed"].capitalize(),
                f"{entry['eth_cost']:.6f} ETH",
                f"${entry['usd_cost']:,.2f} USD",
                f"{results['currency']} {entry['currency_cost']:,.2f}",
            ])

    print("\n🔹 Current Gas Prices (Gwei):")
    for k, v in results["current_gas_prices_gwei"].items():
        print(f"   {k.capitalize():<7}: {v} Gwei")

    print("\n-------------------------------------\n")
    print(tabulate(table, headers=["Speed", "Cost (ETH)", "Cost (USD)", f"Cost ({results['currency']})"], tablefmt="pretty"))


if __name__ == "__main__":
    main()
