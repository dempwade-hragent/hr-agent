# 🚀 HR Assistant - Complete Installation & Setup Guide

Welcome! This guide will walk you through everything you need to get your HR Assistant up and running. No technical experience required!

---

## 📋 Table of Contents

1. [What You're Installing](#what-youre-installing)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Installation](#step-by-step-installation)
4. [Running the Application](#running-the-application)
5. [Using the Web Interface](#using-the-web-interface)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)

---

## 🎯 What You're Installing

The HR Assistant is a chatbot that answers employee questions using your HR data. It consists of:

- **Backend (Python)**: The "brain" that processes questions and queries your CSV database
- **Frontend (Web)**: A beautiful chat interface you use in your web browser
- **Database (CSV)**: Your employee data file on your desktop

---

## ✅ Prerequisites

Before you start, you need:

### 1. Python (Version 3.7 or higher)

**Check if you have Python:**
- **Windows**: Open Command Prompt and type `python --version`
- **Mac/Linux**: Open Terminal and type `python3 --version`

**Don't have Python?**
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
  - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation!
- **Mac**: Download from [python.org](https://www.python.org/downloads/) or use `brew install python3`
- **Linux**: Use `sudo apt-get install python3` (Ubuntu/Debian)

### 2. Your HR Data CSV File

Make sure your CSV file has these exact column names:
```
First Name, Gender, Start Date, Last Login Time, Salary, Bonus %, Senior Management, Team, Days Off Remaining, Town, EmployeeID
```

---

## 📥 Step-by-Step Installation

### Step 1: Download All Files

Download all these files to a single folder on your computer (e.g., `C:\HR-Assistant` or `~/HR-Assistant`):

```
HR-Assistant/
├── hr_agent_sdk.py          # The main SDK code
├── backend.py               # The web server
├── frontend.html            # The web interface
├── requirements.txt         # List of dependencies
├── sample_hr_data.csv       # Example data (for testing)
├── README.md                # Documentation
├── example_usage.py         # Code examples
├── chatbot.py              # Command-line version
└── INSTALLATION.md          # This file
```

### Step 2: Open Terminal/Command Prompt

**Windows:**
1. Press `Windows Key + R`
2. Type `cmd` and press Enter
3. Navigate to your folder: `cd C:\HR-Assistant`

**Mac:**
1. Press `Cmd + Space` and type "Terminal"
2. Navigate to your folder: `cd ~/HR-Assistant`

**Linux:**
1. Open Terminal (Ctrl + Alt + T)
2. Navigate to your folder: `cd ~/HR-Assistant`

### Step 3: Install Dependencies

Copy and paste this command, then press Enter:

**Windows:**
```bash
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
pip3 install -r requirements.txt
```

This installs:
- `pandas` - For reading CSV files
- `flask` - For the web server
- `flask-cors` - For connecting frontend to backend

**Expected Output:**
```
Successfully installed pandas-2.1.0 flask-3.0.0 flask-cors-4.0.0
```

### Step 4: Configure Your CSV File Path

Open `backend.py` in any text editor (Notepad, TextEdit, VS Code, etc.) and find this line near the top:

```python
CSV_PATH = "sample_hr_data.csv"
```

Change it to point to your actual CSV file. For example:

**Windows:**
```python
CSV_PATH = r"C:\Users\YourName\Desktop\my_hr_data.csv"
```
Note: The `r` before the string is important for Windows paths!

**Mac/Linux:**
```python
CSV_PATH = "/Users/YourName/Desktop/my_hr_data.csv"
```

Save the file.

---

## 🎮 Running the Application

### Method 1: Web Interface (Recommended)

This gives you a beautiful chat interface in your browser!

**Step 1: Start the Backend Server**

In your terminal/command prompt:

**Windows:**
```bash
python backend.py
```

**Mac/Linux:**
```bash
python3 backend.py
```

**You should see:**
```
============================================================
🚀 HR Assistant Backend Server
============================================================
📊 CSV File: sample_hr_data.csv
🌐 Server: http://localhost:5000
💡 Open frontend.html in your browser to use the app
============================================================

 * Running on http://127.0.0.1:5000
```

**⚠️ Keep this window open!** The server needs to run while you use the app.

**Step 2: Open the Frontend**

1. Find `frontend.html` in your folder
2. Double-click it to open in your browser
   - Or right-click → Open With → Chrome/Firefox/Safari

**You're ready to go!** 🎉

### Method 2: Command-Line Interface

For a simpler, text-based interface:

**Windows:**
```bash
python chatbot.py
```

**Mac/Linux:**
```bash
python3 chatbot.py
```

This will prompt you to enter your Employee ID or First Name, then you can ask questions!

### Method 3: Python Code Integration

To use the SDK in your own Python code:

```python
from hr_agent_sdk import HRAgent

# Initialize with your CSV
agent = HRAgent("path/to/your/data.csv")

# Ask a question
result = agent.answer_question(
    "What's my salary?",
    employee_id="EMP001"
)

print(result['answer'])
```

---

## 💬 Using the Web Interface

### 1. Sign In

When you open the web interface, you'll see a sign-in form on the left.

Enter either:
- **Employee ID** (e.g., "EMP001")
- **OR First Name** (e.g., "John")

Click "Start Chatting"

### 2. Ask Questions

You can either:
- **Type your question** in the chat box at the bottom
- **Click a quick question** from the sidebar

Example questions:
- "What's my salary?"
- "How many days off do I have?"
- "What is my bonus percentage?"
- "Do I work on-site or remote?"
- "What team am I on?"

### 3. Get Answers

The bot will respond with your information from the CSV database!

### 4. Switch Users

Click "Switch User" in the sidebar to sign in as a different employee.

---

## 🔧 Troubleshooting

### Problem: "Command not found" or "Python not recognized"

**Solution:** Python isn't installed or not in your PATH.
- Reinstall Python and check "Add Python to PATH"
- Or use full path: `C:\Python311\python.exe backend.py`

### Problem: "No module named 'pandas'" (or flask, etc.)

**Solution:** Dependencies not installed.
```bash
pip install pandas flask flask-cors
```

### Problem: "CSV file not found"

**Solution:** Check your CSV_PATH in `backend.py`
- Use absolute paths (full path from C:\ or /)
- Use `r"..."` for Windows paths
- Make sure the file exists at that location

### Problem: "Employee not found"

**Solution:** 
- Check Employee ID matches exactly (case-sensitive)
- Check First Name matches exactly (case-sensitive)
- Verify the employee exists in your CSV

### Problem: Frontend says "Can't connect to server"

**Solution:** 
- Make sure `backend.py` is running
- Check that you see "Running on http://127.0.0.1:5000"
- Try refreshing the frontend page

### Problem: Port 5000 already in use

**Solution:** Change the port in `backend.py`:
```python
app.run(debug=True, port=5001)  # Use 5001 instead
```

Then update the frontend.html to use the new port:
```javascript
const response = await fetch('http://localhost:5001/api/ask', {
```

### Problem: CORS errors in browser console

**Solution:** Make sure flask-cors is installed:
```bash
pip install flask-cors
```

---

## ⚙️ Advanced Configuration

### Use a Different Port

Edit `backend.py`, last line:
```python
app.run(debug=True, port=8080)  # Change to your preferred port
```

### Add More Question Patterns

Edit `hr_agent_sdk.py`, find `QueryParser.PATTERNS` and add:
```python
'custom_intent': [
    r'your regex pattern',
    r'another pattern'
]
```

### Customize the Frontend Design

Edit `frontend.html` - all styling is in the `<style>` section!

Change colors by editing CSS variables:
```css
:root {
    --primary: #FF6B35;  /* Main brand color */
    --secondary: #004E89; /* Secondary color */
    /* ... etc */
}
```

### Enable Debug Mode

In `backend.py`, debug mode is already enabled:
```python
app.run(debug=True, port=5000)
```

This will auto-reload when you change code!

### Run on Network (Access from Other Computers)

In `backend.py`, change:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

Then access from other computers using:
```
http://YOUR_COMPUTER_IP:5000
```

---

## 📱 Deployment Options

### Option 1: Local Network Only
Keep the setup as-is. Only computers on your local network can access it.

### Option 2: Cloud Deployment (Heroku, AWS, etc.)
1. Add a `Procfile` for Heroku:
   ```
   web: python backend.py
   ```
2. Update frontend.html to use your cloud URL instead of localhost
3. Deploy using your cloud provider's instructions

### Option 3: Desktop Application (Electron)
Wrap the frontend in Electron to create a standalone desktop app!

---

## 🎓 Quick Reference Commands

### Start the web server:
```bash
python backend.py
```

### Test with command-line interface:
```bash
python chatbot.py
```

### Run example code:
```bash
python example_usage.py
```

### Run tests (if you installed pytest):
```bash
pytest test_hr_agent.py
```

### Stop the server:
Press `Ctrl + C` in the terminal

---

## 📞 Getting Help

### Check the logs
When the backend is running, it prints helpful messages. Look for:
- ✓ = Success
- ✗ = Error
- Error messages with details

### Common Error Messages

| Error | What it means | Solution |
|-------|---------------|----------|
| "CSV file not found" | Can't find your data file | Check CSV_PATH |
| "Employee not found" | Invalid ID/name | Check spelling, case |
| "Address already in use" | Port 5000 busy | Change port or kill process |
| "Module not found" | Missing dependency | Run pip install |

---

## 🎉 You're All Set!

Your HR Assistant should now be running! 

**Remember:**
1. Start the backend first (`python backend.py`)
2. Open frontend.html in your browser
3. Sign in with Employee ID or First Name
4. Start asking questions!

**Need more help?** Check the main README.md for detailed API documentation.

Enjoy your new HR Assistant! 🚀
