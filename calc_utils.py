def calculate_gas_cost(gas_used, gas_price_gwei, eth_price):
    """Calculate gas cost in ETH and fiat currency."""
    gas_cost_eth = gas_used * gas_price_gwei * 1e-9
    gas_cost_fiat = gas_cost_eth * eth_price
    return gas_cost_eth, gas_cost_fiat
