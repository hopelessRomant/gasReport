import requests
import os
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
if not ETHERSCAN_API_KEY:
    raise ValueError("❌ ETHERSCAN_API_KEY not found in .env file")

def safe_api_request(url, key):
    try:
        response = requests.get(url, timeout=10).json()
        if response.get("status") == "1" and "result" in response:
            return response["result"]
        else:
            print(f"⚠️ API Error in {key}: {response}")
            return None
    except requests.RequestException as e:
        print(f"❌ Network Error in {key}: {e}")
        return None

def get_gas_prices():
    url = f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={ETHERSCAN_API_KEY}"
    result = safe_api_request(url, "get_gas_prices")
    if not result:
        return {"safe": 0, "average": 0, "fast": 0}
    return {
        "safe": float(result.get("SafeGasPrice", 0)),
        "average": float(result.get("ProposeGasPrice", 0)),
        "fast": float(result.get("FastGasPrice", 0)),
    }

def get_eth_price_usd():
    url = f"https://api.etherscan.io/api?module=stats&action=ethprice&apikey={ETHERSCAN_API_KEY}"
    result = safe_api_request(url, "get_eth_price_usd")
    return float(result.get("ethusd", 0)) if result else 0

def get_currency_rates():
    url = "https://api.exchangerate.host/latest?base=USD"
    try:
        response = requests.get(url, timeout=10).json()
        return response.get("rates", {})
    except requests.RequestException as e:
        print(f"❌ Currency API error: {e}")
        return {}

def main():
    gas_prices = get_gas_prices()
    eth_price_usd = get_eth_price_usd()
    rates = get_currency_rates()

    try:
        gas_used = float(input("Enter gas used: "))
    except ValueError:
        print("❌ Invalid gas input. Please enter a number.")
        return

    currency = input("Enter target currency (default INR): ").upper() or "INR"
    usd_to_currency = rates.get(currency, 0)

    if usd_to_currency == 0:
        print(f"⚠️ Currency '{currency}' not found. Defaulting to INR.")
        usd_to_currency = rates.get("INR", 0)

    table = []
    for speed, gwei in gas_prices.items():
        if gwei == 0 or eth_price_usd == 0 or usd_to_currency == 0:
            table.append([speed.capitalize(), "API Error", "-", "-"])
            continue

        gas_cost_eth = gas_used * gwei * 1e-9  # Convert to ETH
        gas_cost_usd = gas_cost_eth * eth_price_usd
        gas_cost_cur = gas_cost_usd * usd_to_currency

        table.append([
            speed.capitalize(),
            f"{gas_cost_eth:.6f} ETH",
            f"${gas_cost_usd:,.2f} USD",
            f"{currency} {gas_cost_cur:,.2f}",
        ])

    print("\n🔹 Current Gas Prices (Gwei):")
    for k, v in gas_prices.items():
        print(f"   {k.capitalize():<7}: {v} Gwei")

    print("\n-------------------------------------\n")
    print(tabulate(table, headers=["Speed", "Cost (ETH)", "Cost (USD)", f"Cost ({currency})"], tablefmt="pretty"))

if __name__ == "__main__":
    main()
