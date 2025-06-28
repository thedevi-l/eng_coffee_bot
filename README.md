# ☕ Random Coffee Telegram Bot

A Telegram bot to help English learners find conversation partners based on interests and language level.  
This version is optimized for **deployment on Replit**.

## 💡 Features

- Collects user data: name, English level, interests, and goals
- Stores all data in a local SQLite database (`users.db`)
- Matches users manually with `/match` or "🔍 Find a partner" button
- Automatically sends new matches every **Saturday**
- Avoids matching users with themselves
- Works continuously thanks to a `keep_alive.sh` loop
- Secure token management via **Replit Secrets**

### 📦 Files

| File            | Description                                  |
|-----------------|----------------------------------------------|
| `main.py`       | Main bot logic                               |
| `database.py`   | SQLite database handling                     |
| `requirements.txt` | Python dependencies                      |
| `keep_alive.sh` | Keeps the bot running continuously           |

### ⏰ Weekly Auto-Matching

The bot uses APScheduler to automatically match and message users every Saturday based on similar interests and level.

#### 🚀 How to Deploy on Replit

### 1. **Create a new Python Repl**
- Go to [Replit](https://replit.com/)
- Click "Create Repl" → Choose **Python**

### 2. **Upload the files**
- Upload the following files into your Replit project:
  - `main.py`
  - `database.py`
  - `requirements.txt`
  - `keep_alive.sh`
  - `README.md` (optional)
- Or simply upload the `.zip` archive and extract it in Replit.

### 3. **Add your Bot Token**
- Go to the **Secrets** tab (🔑 on left sidebar)
- Add a new secret:
  - **Key:** `BOT_TOKEN`
  - **Value:** your Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### 4. **Set the Run Command**

Click the ⚙️ “⋮” next to `main.py` → "Show hidden files" → go to `.replit` file and set:

```replit


