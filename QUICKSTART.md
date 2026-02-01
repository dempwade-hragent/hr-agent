# 🚀 QUICK START GUIDE

Get your HR Assistant running in 3 easy steps!

---

## For Complete Beginners 👶

### Step 1: Install Python (One-Time Setup)

**Windows:**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python (latest version)
3. Run the installer
4. ✅ **IMPORTANT**: Check the box "Add Python to PATH"
5. Click "Install Now"

**Mac:**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python for macOS
3. Open the downloaded file and install

**Linux:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
```

---

### Step 2: Install Dependencies (One-Time Setup)

Open Terminal/Command Prompt in the HR-Assistant folder:

**Windows:**
- Hold Shift + Right-click in the folder → "Open PowerShell window here"
- Type: `pip install -r requirements.txt` → Press Enter

**Mac/Linux:**
- Right-click folder → "New Terminal at Folder"
- Type: `pip3 install -r requirements.txt` → Press Enter

---

### Step 3: Run the App! 🎉

**Option A: Use the Startup Script (Easiest!)**

**Windows:**
- Double-click `start_windows.bat`

**Mac/Linux:**
- Double-click `start_mac_linux.sh`
- (If it doesn't work, right-click → Open With → Terminal)

**Option B: Manual Start**

**Windows:**
```bash
python backend.py
```

**Mac/Linux:**
```bash
python3 backend.py
```

Then open `frontend.html` in your browser!

---

## 📝 Configure Your Data

Before running, edit `backend.py` to point to your CSV file:

```python
CSV_PATH = "sample_hr_data.csv"  # Change this line
```

**Windows example:**
```python
CSV_PATH = r"C:\Users\YourName\Desktop\hr_data.csv"
```

**Mac example:**
```python
CSV_PATH = "/Users/YourName/Desktop/hr_data.csv"
```

---

## ✅ How to Use

1. **Start the backend** (see Step 3 above)
2. **Open frontend.html** in Chrome, Firefox, or Safari
3. **Sign in** with Employee ID or First Name
4. **Start chatting!**

---

## 🆘 Troubleshooting

### "Python not found"
→ Install Python (see Step 1) and check "Add to PATH"

### "Module not found"
→ Run: `pip install -r requirements.txt`

### "Can't connect to server"
→ Make sure backend.py is running (see green text in terminal)

### "Employee not found"
→ Check spelling and make sure employee exists in your CSV

---

## 📱 Features

- ✅ Beautiful chat interface
- ✅ Instant answers about salary, PTO, bonus, team, location
- ✅ Works with your existing CSV file
- ✅ Quick question buttons
- ✅ No internet required (runs locally)

---

## 💡 Example Questions

Try asking:
- "What's my salary?"
- "How many days off do I have?"
- "What is my bonus percentage?"
- "Do I work on-site or remote?"
- "What team am I on?"

---

## 🎨 What You'll See

When you open frontend.html, you'll see:

```
┌─────────────────────────────────────────────┐
│           HR ASSISTANT                       │
│   Your Personal HR Companion                 │
├──────────────┬──────────────────────────────┤
│              │                               │
│  Sign In     │     💬 Chat Area              │
│  Box         │                               │
│              │     Start chatting!           │
│  Quick       │                               │
│  Questions   │                               │
│              │                               │
└──────────────┴──────────────────────────────┘
```

---

## 📚 Need More Help?

See **INSTALLATION.md** for detailed instructions!

---

That's it! You're ready to use your HR Assistant! 🎊
