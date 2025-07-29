import requests
import os
from dotenv import load_dotenv

load_dotenv()

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
if not ETHERSCAN_API_KEY:
    raise ValueError("❌ ETHERSCAN_API_KEY not found in .env file")

def safe_api_request(url, key):
    try:
        response = requests.get(url, timeout=10).json()
        if "result" in response:
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

def get_usd_to_inr():
    url = "https://api.exchangerate.host/latest?base=USD&symbols=INR"
    try:
        response = requests.get(url, timeout=10).json()
        return float(response.get("rates", {}).get("INR", 0))
    except requests.RequestException as e:
        print(f"❌ Currency API error: {e}")
        return 0

def main():
    gas_prices = get_gas_prices()
    eth_price_usd = get_eth_price_usd()
    usd_to_inr = get_usd_to_inr()

    try:
        gas_used = float(input("Enter gas used: "))
    except ValueError:
        print("❌ Invalid gas input. Please enter a number.")
        return

    print("\n🔹 Current Gas Prices (Gwei):")
    for k, v in gas_prices.items():
        print(f"   {k.capitalize():<7}: {v} Gwei")

    print("\n-------------------------------------\n")

    for speed, gwei in gas_prices.items():
        if gwei == 0 or eth_price_usd == 0 or usd_to_inr == 0:
            print(f"⚠️ Skipping {speed.capitalize()} (API error)")
            continue

        gas_cost_eth = gas_used * gwei * 1e-9  # Convert to ETH
        gas_cost_usd = gas_cost_eth * eth_price_usd
        gas_cost_inr = gas_cost_usd * usd_to_inr

        print(f"💰 {speed.capitalize()} Gas Cost:")
        print(f"   {gas_cost_eth:.6f} ETH")
        print(f"   ₹{gas_cost_inr:,.2f} INR\n")

if __name__ == "__main__":
    main()
