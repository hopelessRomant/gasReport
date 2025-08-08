
---

# gasReport 🚀

gasReport is your chill PyQt6 app running in WSL2/Linux that does one thing well: take your input gas amount + currency ISO code, talk to Etherscan, and show you the gas prices in ETH and your fave currency — safe, average, and fast speeds included. It’s simple, clean, and gets the job done without drama.

---

## What You Need Before You Start

* WSL2 (or any Linux, but WSL2 is tested & loved)
* Python 3.8+ (latest version works fine)
* An Etherscan API key (store it safely, not that I care :-)..)

---

## Quick Setup Guide

1. **Make sure WSL2 + Python are installed** — If you’re here, you probably know this. If not, Google it or ask ChatGPT.
2. Clone this repo:

   ```bash
   git clone https://github.com/tincan1596/gasReport
   cd gasReport
   ```
3. Copy `.env.example` to `.env` and put your `ETHERSCAN_API_KEY` inside:

   ```bash
   cp .env.example .env
   # Edit .env and add your key
   ```
4. Make the installer script executable:

   ```bash
   chmod +x install.sh
   ```
5. Run the installer — it sets up everything for you:

   ```bash
   ./install.sh
   ```
6. Restart the terminal or run `source ~/.bashrc` , now you can run the app from any directory at any time by just typing in:

   ```bash
   gasReport
   ```

   Boom! The app (MAY) launch, ask chat GPT if an error pops up :-)...

---

## How It Works

* You feed it the total gas amount (from wherever you want — foundry test, another tool, you do you).
* Enter your preferred currency’s ISO code (like USD, INR, EUR, whatever).
* gasReport hits Etherscan API, grabs the latest gas prices in ETH.
* Converts that ETH gas price to your currency.
* Shows you Safe, Average, and Fast gas price options.

No rocket science, just quick conversions.

---

## Troubleshooting / Help

If something breaks or looks funky — try turning it off and on again. Still stuck? Hit up ChatGPT or your favorite AI assistant for a quick fix. Seriously, that’s the best support you’re gonna get.

---

## Heads Up

* Keep your `ETHERSCAN_API_KEY` private. Don’t leak it or share it like free candy.
* This app is still in chill mode — no wild error handling or fancy alerts. If it crashes, blame the internet or your input.
* Future plans? Maybe a Windows executable so you don’t have to bother with WSL2 — stay tuned.

---

## License

MIT License — do whatever you want, just don’t sue me.

---

## Directory Breakdown (If You Care)

```
├── LICENSE  
├── __pycache__ (ignored, because duh)  
├── api_utils.py  # fetches data from Etherscan  
├── app.py        # PyQt6 app GUI  
├── calc_utils.py # gas price and currency conversion logic  
├── install.sh    # sets up your environment & dependencies  
├── main.py       # processes JSON data for the app  
├── readme.md     # this file, obviously  
├── requirements.txt # Python dependencies  
```

---

That’s it. Fast, easy, and actually useful.

---
