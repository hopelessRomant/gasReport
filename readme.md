Here’s the **updated README.md** that includes the `.env` setup for the API key:

---

# 🚀 GasReport – Ethereum Gas Fee Calculator

A simple Python script to fetch **real-time gas prices** from Etherscan, calculate gas fees in **ETH & INR**, and display the cost for Safe, Average, and Fast gas prices.

---

## 📌 Features

✅ Fetches **Safe / Average / Fast gas prices**
✅ Gets **real-time ETH/USD price**
✅ Converts ETH cost to **INR (₹)**
✅ Uses **secure `.env` file** for API key (never push secrets to GitHub)
✅ Works inside a **virtual environment** for clean dependency management

---

## 🔹 1. Setup Instructions

### **1️⃣ Install Python (WSL2 / Ubuntu)**

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

---

### **2️⃣ Create Project Folder**

```bash
mkdir -p ~/sidequest/GasReport
cd ~/sidequest/GasReport
```

---

### **3️⃣ Create Virtual Environment (.venv)**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### **4️⃣ Install Dependencies**

```bash
pip install requests python-dotenv
pip freeze > requirements.txt
```

---

### **5️⃣ Create `.env` File (DO NOT COMMIT THIS FILE)**

```bash
nano .env
```

Inside `.env` add:

```
ETHERSCAN_API_KEY=your_api_key_here
```

Save (`Ctrl+O`, `Enter`) and exit (`Ctrl+X`).

---

### **6️⃣ Create `.gitignore`**

```bash
nano .gitignore
```

Paste this:

```
.venv/
.env
__pycache__/
*.pyc
*.pyo
*.pyd
.vscode/
.idea/
.DS_Store
Thumbs.db
```

---

### **7️⃣ Add Your Python Script**

Save the final version of `gas_calculator.py` in this folder.

---

## 🔹 2. Running the Program

Activate virtual environment:

```bash
cd ~/sidequest/GasReport
source .venv/bin/activate
```

Run the script:

```bash
python3 gas_calculator.py
```

Enter gas used (e.g., `120000`), and it will show:
✅ Gas prices in Gwei
✅ Total cost in ETH
✅ Converted price in ₹ INR

---

## 🔹 3. GitHub Setup

```bash
git init
git branch -M main
git remote add origin git@github.com:YOUR_USERNAME/GasReport.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

✅ `.env` and `.venv` will **NOT be pushed** because they are in `.gitignore`.

---

## 🔒 Security Notes

✅ **Never commit `.env` or API keys**
✅ If you accidentally pushed `.env`, **revoke the key from Etherscan and create a new one**

---

Do you want me to **combine this README.md with the exact final `gas_calculator.py` code** so you can copy-paste **both at once?**
