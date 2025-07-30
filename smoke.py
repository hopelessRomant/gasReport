import requests
import os
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
if not ETHERSCAN_API_KEY:
    raise ValueError(" ETHERSCAN_API_KEY not found in .env file")


def safe_api_request(url, key):
    try:
        response = requests.get(url, timeout=10).json()
        if isinstance(response, dict):
            return response
        else:
            print(f" API Error in {key}: {response}")
            return None
    except requests.RequestException as e:
        print(f" Network Error in {key}: {e}")
        return None


def get_gas_prices():
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


def get_eth_prices():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd,inr,eur,gbp,jpy"
    result = safe_api_request(url, "get_eth_prices")
    if not result or "ethereum" not in result:
        return {}

    return result["ethereum"]  # Example: {"usd": 3050, "inr": 250000, ...}


def main():
    gas_prices = get_gas_prices()
    eth_prices = get_eth_prices()

    if not eth_prices:
        print(" Failed to fetch ETH prices. Try again later.")
        return

    try:
        gas_used = float(input("Enter gas used: "))
    except ValueError:
        print(" Invalid gas input. Please enter a number.")
        return

    currency = input("Enter target currency (default INR): ").lower() or "inr"

    if currency not in eth_prices:
        print(f" Currency '{currency.upper()}' not available. Defaulting to INR.")
        currency = "inr"

    table = []
    eth_price_usd = eth_prices.get("usd", 0)
    eth_price_target = eth_prices.get(currency, 0)

    for speed, gwei in gas_prices.items():
        if gwei == 0 or eth_price_usd == 0 or eth_price_target == 0:
            table.append([speed.capitalize(), "API Error", "-", "-"])
            continue

        gas_cost_eth = gas_used * gwei * 1e-9
        gas_cost_usd = gas_cost_eth * eth_price_usd
        gas_cost_cur = gas_cost_eth * eth_price_target

        table.append([
            speed.capitalize(),
            f"{gas_cost_eth:.6f} ETH",
            f"${gas_cost_usd:,.2f} USD",
            f"{currency.upper()} {gas_cost_cur:,.2f}",
        ])

    print("\n🔹 Current Gas Prices (Gwei):")
    for k, v in gas_prices.items():
        print(f"   {k.capitalize():<7}: {v} Gwei")

    print("\n-------------------------------------\n")
    print(tabulate(table, headers=["Speed", "Cost (ETH)", "Cost (USD)", f"Cost ({currency.upper()})"], tablefmt="pretty"))


if __name__ == "__main__":
    main()
