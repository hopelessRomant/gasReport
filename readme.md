
---

# Gas Price Calculator (Desktop App)

A local desktop application built with **PyQt6** that fetches Ethereum gas prices from Etherscan and ETH conversion rates from CoinGecko. The app calculates total gas costs (in ETH and the user’s preferred fiat currency) and updates automatically every 30 seconds.

---

## 🚀 Features

1. Enter **gas used** (e.g. 21000) and an **ISO currency code** (e.g. USD, INR, EUR).
2. Click **Calculate** to display gas costs in ETH and fiat currency.
3. App refreshes automatically every **30 seconds**, showing a countdown before each update.
4. Text for “Safe” gas speed is displayed in **green**, “Average” in **blue**, and “Fast” in **red**.
5. Clean, dark-themed interface with resizable layout.

---

## 📁 Repository Structure

```
gas_price_app/
├── api_utils.py       # API fetch and caching logic
├── calc_utils.py      # (Optional) separate calculation logic
├── main.py            # Data retrieval and formatting logic
├── app.py             # GUI application
├── requirements.txt   # Python dependencies
└── .env.example       # Example template for environment variables
```

---

## 🧰 Setup & Run Instructions

### 1. Clone the repository

```bash
git clone https://github.com/tincan1596/GasReport
cd GasReport
```

### 2. Install Python dependencies

Make sure you’re using **Python 3.7+** and run:

```bash
pip install -r requirements.txt
```

### 3. Create API key file

Copy the example file and set your Etherscan API key:

```bash
cp .env.example .env
```

Open `.env` and replace placeholder:

```
ETHERSCAN_API_KEY=your_real_key_here
```

### 4. Run the application

```bash
python3 app.py
```

* A GUI window will launch.
* Enter **gas used** and **ISO currency code**, then click **Calculate**.
* The table populates below and refreshes every **30 seconds**.

---

## ⚙️ Application Flow

* **`app.py`** handles the graphical interface, inputs, button, table, countdown logic, and periodic refresh.
* **`main.py`** contains `get_gas_costs_json()` to fetch gas and ETH data.
* **`api_utils.py`** manages API interactions and rate-limited caching for CoinGecko calls.
* **`calc_utils.py`** (optional) can house modular functions for calculations if needed.

---

## 💡 Notes

* No external settings are saved—each run starts fresh.
* If you enter an uncommon or unsupported currency code, the app will default to USD or display an error.
* Ensure your Etherscan API key is valid to avoid API errors.
* This is a local desktop application and not a web app—no browser or server needed.

---

## 🧭 Troubleshooting

* **API error messages** usually point to:

  * Invalid or expired API key.
  * Exceeding free rate limits for CoinGecko (relevant if refresh is too frequent).
* **GUI is blank or not resizing**:

  * Ensure `app.py` has not been modified and includes correct layout settings.
  * Restart the app after resizing the terminal window.
* **Currency not recognized**:

  * Check standard ISO codes (e.g. USD, EUR, INR). They must be lowercase in input.

---

## 🎯 Future Enhancements

* Packaging as a standalone executable (`.exe` for Windows, `.app` for macOS).
* Localization support for multiple currencies beyond USD.
* Export results to CSV or JSON for further analysis.

---

Thank you for checking out the Gas Price Calculator. Feel free to open issues, fork the repo, and contribute improvements!
