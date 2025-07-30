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

    usd_price = get_eth_prices("usd").get("usd", 0)
    target_price = eth_prices.get(currency, 0)

    results = {
        "currency": currency.upper(),
        "gas_costs": [],
        "current_gas_prices_gwei": gas_prices,
    }

    for speed, gwei in gas_prices.items():
        if gwei == 0 or target_price == 0:
            entry = {
                "speed": speed,
                "eth_cost": None,
                "currency_cost": None,
                "error": "API Error"
            }
            if currency == "usd":
                entry["usd_cost"] = None
            results["gas_costs"].append(entry)
            continue

        gas_eth = gas_used * gwei * 1e-9
        gas_cur = gas_eth * target_price
        gas_usd = gas_eth * usd_price if currency == "usd" else None

        entry = {
            "speed": speed,
            "eth_cost": round(gas_eth, 8),
            "currency_cost": round(gas_cur, 2),
        }

        if currency == "usd":
            entry["usd_cost"] = round(gas_usd, 2)

        results["gas_costs"].append(entry)

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

    # Build table dynamically
    table = []
    for entry in results["gas_costs"]:
        if entry.get("error"):
            if currency == "usd":
                table.append([entry["speed"].capitalize(), "API Error", "-"])
            else:
                table.append([entry["speed"].capitalize(), "API Error", "-"])
        else:
            if currency == "usd":
                table.append([
                    entry["speed"].capitalize(),
                    f"{entry['eth_cost']:.6f} ETH",
                    f"${entry['usd_cost']:,.2f} USD"
                ])
            else:
                table.append([
                    entry["speed"].capitalize(),
                    f"{entry['eth_cost']:.6f} ETH",
                    f"{results['currency']} {entry['currency_cost']:,.2f}",
                ])

    # Print gas prices
    print("\n🔹 Current Gas Prices (Gwei):")
    for k, v in results["current_gas_prices_gwei"].items():
        print(f"   {k.capitalize():<7}: {v} Gwei")

    print("\n-------------------------------------\n")

    # Print table with correct headers
    if currency == "usd":
        print(tabulate(table, headers=["Speed", "Cost (ETH)", "Cost (USD)"], tablefmt="pretty"))
    else:
        print(tabulate(table, headers=["Speed", "Cost (ETH)", f"Cost ({results['currency']})"], tablefmt="pretty"))


if __name__ == "__main__":
    main()
