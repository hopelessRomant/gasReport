import requests

ETHERSCAN_API_KEY = "YOUR_API_KEY"  # 🔹 Replace with your API key

def get_gas_prices():
    url = f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url).json()
    result = response["result"]
    return {
        "safe": float(result["SafeGasPrice"]),
        "average": float(result["ProposeGasPrice"]),
        "fast": float(result["FastGasPrice"]),
    }

def get_eth_price_usd():
    url = f"https://api.etherscan.io/api?module=stats&action=ethprice&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url).json()
    return float(response["result"]["ethusd"])

def get_usd_to_inr():
    url = "https://api.exchangerate.host/latest?base=USD&symbols=INR"
    response = requests.get(url).json()
    return float(response["rates"]["INR"])

def main():
    gas_prices = get_gas_prices()
    eth_price_usd = get_eth_price_usd()
    usd_to_inr = get_usd_to_inr()

    gas_used = float(input("Enter gas used: "))

    print("\n🔹 Current Gas Prices (Gwei):")
    print(f"   Safe    : {gas_prices['safe']} Gwei")
    print(f"   Average : {gas_prices['average']} Gwei")
    print(f"   Fast    : {gas_prices['fast']} Gwei\n")

    for speed, gwei in gas_prices.items():
        gas_cost_eth = gas_used * gwei * 1e-9
        gas_cost_usd = gas_cost_eth * eth_price_usd
        gas_cost_inr = gas_cost_usd * usd_to_inr

        print(f"💰 {speed.capitalize()} Gas Cost:")
        print(f"   {gas_cost_eth:.6f} ETH")
        print(f"   ₹{gas_cost_inr:.2f} INR\n")

if __name__ == "__main__":
    main()
