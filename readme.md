
---

# Gas Fee Calculator

A lightweight Python script that fetches **real-time Ethereum gas prices** from the Etherscan API and calculates **transaction fees in ETH, USD, and other currencies** using CoinGecko.
The script is simple to set up and run, making it useful for developers testing and estimating smart contract gas costs.

---

## 📌 Features

* Fetches **Safe, Average, and Fast gas prices** from Etherscan.
* Calculates **transaction costs** in ETH, USD, and multiple fiat currencies.
* Uses **CoinGecko API (no API key required)** for currency conversion.
* Outputs a **clean, formatted table** for better readability.
* Works on **Linux/WSL2 environments** (recommended for smart contract developers).

---

## 📌 Prerequisites

* **Python 3.12.3** or higher (Linux/WSL recommended)
* A valid **Etherscan API key**

---

## 📌 Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/tincan1596/GasReport
cd GasReport
```

### 2️⃣ Create a Virtual Environment

```bash
python3 -m venv .venv
```

### 3️⃣ Activate the Virtual Environment

```bash
source .venv/bin/activate
```

### 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 5️⃣ Create a `.env` File

Inside the project root, create a file named `.env` and add:

```
ETHERSCAN_API_KEY=your_etherscan_api_key_here
```

Replace `your_etherscan_api_key_here` with your actual Etherscan API key.

---

## 📌 How to Run

Activate the virtual environment and run:

```bash
source .venv/bin/activate
python3 smoke.py
```

You will be prompted to:

1. Enter the **gas used** for your transaction (e.g. `120000`)
2. Enter the **target currency** (e.g. `INR`, `USD`, `EUR`, `GBP`, `JPY`). Press Enter to default to INR.

---

## 📌 Example Output

```
Enter gas used: 1191956
Enter target currency (default INR): INR

🔹 Current Gas Prices (Gwei):
   Safe   : 1.31 Gwei
   Average: 1.31 Gwei
   Fast   : 1.46 Gwei

-------------------------------------

+---------+------------+------------+------------+
|  Speed  | Cost (ETH) | Cost (USD) | Cost (INR) |
+---------+------------+------------+------------+
|  Safe   | 0.001563   | $5.10      | INR 425.65 |
| Average | 0.001563   | $5.10      | INR 425.70 |
|  Fast   | 0.001741   | $5.68      | INR 473.60 |
+---------+------------+------------+------------+
```

---

## 📌 Notes

* Supported currencies can be extended by modifying the CoinGecko API URL in the script.
* Ensure that you have a stable internet connection and a valid Etherscan API key in your `.env` file.

---

