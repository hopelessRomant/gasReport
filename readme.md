# GasReport – Ethereum Gas Fee Calculator  

A Python tool to fetch **real-time Ethereum gas prices**, calculate transaction costs in **ETH and INR**, and display Safe, Average, and Fast fee estimates.

---

## 📦 Setup (For Users Cloning the Repository)

### 1️⃣ Clone the Repository
```bash
git clone git@github.com:YOUR_USERNAME/GasReport.git
cd GasReport
````

---

### 2️⃣ Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Create `.env` File

Create a `.env` file in the project root:

```bash
nano .env
```

Paste your Etherscan API key:

```
ETHERSCAN_API_KEY=your_api_key_here
```

Save (`Ctrl+O`, `Enter`) and exit (`Ctrl+X`).

---

### 5️⃣ Run the Script

```bash
python3 smoke.py
```

Enter the **gas used** when prompted, and the script will display:
✅ Gas prices (Safe / Average / Fast)
✅ Cost in ETH
✅ Cost in INR

---

### 🔒 Security

* **Do NOT share your `.env` file or API key.**
* `.env` and `.venv` are already in `.gitignore`.

---

```
```
