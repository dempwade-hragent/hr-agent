# 🔍 STEP-BY-STEP CONNECTION TROUBLESHOOTING

Follow these steps IN ORDER to fix the connection issue.

---

## STEP 1: Verify Backend is Actually Running

### Open a terminal and run:

```bash
python3 backend.py
```

### You MUST see this output:

```
============================================================
🚀 HR Assistant Backend Server
============================================================
📊 CSV File: sample_hr_data.csv
🌐 Server: http://localhost:5000
💡 Open frontend.html in your browser to use the app
============================================================

✓ Loaded HR database with 6 employees
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### ⚠️ IMPORTANT:
- This terminal window MUST stay open
- If you see ANY errors, fix them first before continuing
- The backend must be running BEFORE you open the frontend

**Common errors:**
- "No module named 'flask'" → Run: `pip3 install flask flask-cors`
- "CSV file not found" → Update CSV_PATH in backend.py
- "Port already in use" → Close other programs using port 5000

---

## STEP 2: Test Backend Directly

### While backend is running, run this test:

```bash
python3 test_backend.py
```

### Expected output:

```
Testing: http://localhost:5000/api/health

✓ SUCCESS! Backend is responding
  Status: healthy
  Agent loaded: True

Testing: Asking a sample question...

✓ SUCCESS! Backend answered the question
  Question: What's my salary?
  Answer: John's salary is $85,000.00 per year.
  Intent: salary

✅ BACKEND IS WORKING CORRECTLY!
```

### If you see errors:
- Backend is NOT actually running → Go back to Step 1
- Port 5000 is blocked → Check firewall settings
- Backend crashed → Check for error messages in backend terminal

---

## STEP 3: Test in Web Browser

### Open your web browser and navigate to:

```
http://localhost:5000/api/health
```

### You should see:

```json
{
  "agent_loaded": true,
  "status": "healthy"
}
```

### If you DON'T see this:
- Backend is not running → Go back to Step 1
- Using wrong port → Check backend.py says port 5000
- Browser cache issue → Try incognito/private mode

---

## STEP 4: Check Frontend File

### Make sure you're opening the CORRECT frontend.html:

1. Navigate to your HR-Assistant folder
2. Find `frontend.html` 
3. Right-click → "Get Info" (Mac) or "Properties" (Windows)
4. Check the file size - should be around 35-40 KB
5. Check modified date - should be recent (today's date)

### If the file is old:
- Re-download the frontend.html I provided
- Make sure you saved it in the same folder as backend.py

---

## STEP 5: Open Frontend Correctly

### Do NOT just double-click frontend.html!

Instead:

1. **Make sure backend is running** (see Step 1)
2. Right-click frontend.html
3. Choose "Open With" → Chrome, Firefox, or Safari
4. Check the URL bar - it should show something like:
   ```
   file:///Users/YourName/HR-Assistant/frontend.html
   ```

---

## STEP 6: Check Browser Console

### This is the MOST IMPORTANT step for debugging:

1. Open frontend.html in your browser
2. Press `F12` (or `Cmd + Option + I` on Mac)
3. Click the "Console" tab
4. Try to sign in
5. Look for error messages in RED

### Common console errors and solutions:

**❌ "CORS policy" error:**
```
Access to fetch at 'http://localhost:5000/api/ask' from origin 'null' 
has been blocked by CORS policy
```
**Solution:**
```bash
pip3 install flask-cors
# Then restart backend
```

**❌ "Failed to fetch" or "NetworkError":**
```
Failed to fetch
```
**Solution:** Backend is not running. Go to Step 1.

**❌ "ERR_CONNECTION_REFUSED":**
```
net::ERR_CONNECTION_REFUSED
```
**Solution:** Nothing is listening on port 5000. Backend crashed or wasn't started.

**❌ "Unexpected token" or JSON parse error:**
```
Unexpected token < in JSON at position 0
```
**Solution:** Backend returned HTML instead of JSON. Wrong URL or backend error.

---

## STEP 7: Hard Refresh the Page

Sometimes the browser caches the old frontend code.

### Force refresh:
- **Windows/Linux:** `Ctrl + Shift + R`
- **Mac:** `Cmd + Shift + R`

Or:
- **Windows/Linux:** `Ctrl + F5`
- **Mac:** `Cmd + Shift + Delete` (clear cache) then reload

---

## STEP 8: Try a Different Browser

Test in a different browser:
- Chrome
- Firefox
- Safari
- Edge

Sometimes one browser has security restrictions that block localhost.

---

## STEP 9: Check Firewall/Antivirus

Some firewalls block localhost connections:

### Mac:
- System Preferences → Security & Privacy → Firewall
- Make sure Python is allowed

### Windows:
- Windows Defender Firewall → Allow an app
- Allow Python through the firewall

### Antivirus:
- Temporarily disable to test
- If it works, add Python as an exception

---

## STEP 10: Use the Debugger Script

Run the comprehensive debugger:

```bash
python3 debug_connection.py
```

This will check:
- ✓ Is backend running?
- ✓ Is it responding to HTTP?
- ✓ Are CORS headers present?
- ✓ Can it answer questions?

Follow the suggestions it provides.

---

## 🎯 QUICK CHECKLIST

Before asking for more help, verify:

- [ ] Backend is running (Step 1)
- [ ] Backend test passes (Step 2)
- [ ] Browser health check works (Step 3)
- [ ] Using correct frontend.html (Step 4)
- [ ] Opened frontend correctly (Step 5)
- [ ] Checked browser console for errors (Step 6)
- [ ] Tried hard refresh (Step 7)
- [ ] Tested in different browser (Step 8)

---

## 🆘 Still Not Working?

### Share these details:

1. **Backend output** - Copy/paste what you see when running backend.py
2. **Browser console errors** - Screenshot the Console tab (F12)
3. **Test backend result** - Output from `python3 test_backend.py`
4. **Operating system** - Windows/Mac/Linux
5. **Browser** - Chrome/Firefox/Safari/Edge

### Most likely causes:

1. **Backend not actually running** (90% of cases)
   - Check the terminal - is backend.py still running?
   - Did it crash with an error?
   
2. **CORS not installed** (5% of cases)
   - Run: `pip3 install flask-cors`
   - Restart backend

3. **Browser cache** (3% of cases)
   - Hard refresh or clear cache
   - Try incognito mode

4. **Wrong file** (2% of cases)
   - Using old frontend.html
   - Download the new one again

---

## ✅ Success Indicators

You'll know it's working when:

1. Backend terminal shows:
   ```
   127.0.0.1 - - [DATE TIME] "POST /api/ask HTTP/1.1" 200 -
   ```
   (This appears when frontend makes a request)

2. Browser console shows:
   ```
   (No errors in red)
   ```

3. Frontend displays:
   ```
   Welcome to Dempsey's HR, [Your Name]. I'm here to help...
   ```
