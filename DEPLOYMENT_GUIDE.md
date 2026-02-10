# 🚀 HR Agent - New Deployment Guide (Agents SDK 2025)

## ✅ What Changed

### **Old System (Broken)**
- Manual Assistants API calls
- Complex thread management
- Regex-based intent detection (old version)
- Hard to debug
- Employee lookup failures

### **New System (Clean & Working)**
- OpenAI Agents SDK with `Agent` and `Runner`
- `@function_tool` decorators
- Automatic intent detection
- Clean error handling
- Smart employee finder

---

## 📦 New Files

Replace these files on GitHub:

1. **`hr_agent_sdk_new.py`** → Rename to `hr_agent_sdk_openai.py` (or keep new name)
2. **`backend_new.py`** → Rename to `backend.py`
3. **`requirements_new.txt`** → Rename to `requirements.txt`

---

## ⚠️ IMPORTANT: Agents SDK Package

The example code uses `from agents import Agent, Runner, function_tool`.

**Check which package to install:**

### Option 1: Built into `openai` package (v1.54.0+)
```python
from openai import Agent, Runner, function_tool
```

If this works, your `requirements.txt` is fine as-is.

### Option 2: Separate `agents-sdk` package
```bash
pip install agents-sdk
```
```python
from agents import Agent, Runner, function_tool
```

### Option 3: Check OpenAI docs
Go to: https://platform.openai.com/docs/agents

See which import path they use!

---

## 🔧 Deployment Steps

### **1. Update Files on GitHub**

**Option A: Replace Existing (Recommended)**
1. Go to your repo
2. Delete old `backend.py`
3. Upload `backend_new.py` and rename to `backend.py`
4. Delete old `hr_agent_sdk_openai.py`
5. Upload `hr_agent_sdk_new.py` and rename to `hr_agent_sdk_openai.py`
6. Replace `requirements.txt` with `requirements_new.txt`

**Option B: Keep Both (For Testing)**
1. Upload all three `*_new.py` files
2. Update your Procfile to use `backend_new.py`

### **2. Update Procfile (if needed)**

If you renamed files, Procfile should be:
```
web: hypercorn backend:app --bind 0.0.0.0:$PORT
```

If you kept `_new` suffix:
```
web: hypercorn backend_new:app --bind 0.0.0.0:$PORT
```

### **3. Verify Imports**

Before deploying, check the correct import for Agents SDK:

**Test locally or check OpenAI docs**, then update `hr_agent_sdk_new.py` line 8:

```python
# Option 1: If built into openai package
from openai import Agent, Runner, function_tool, RunContextWrapper

# Option 2: If separate package
from agents import Agent, Runner, function_tool, RunContextWrapper
```

### **4. Deploy to Render**

1. Push to GitHub
2. Render auto-deploys
3. Watch logs for:
   ```
   ✅ HR Agent System initialized
   📊 Employee DataFrame columns: [...]
   📊 First 5 Employee IDs: ['EID2480001', 'EID2480002', ...]
   ```

### **5. Test**

1. Go to your site
2. Login with `EID2480002` or `Thomas`
3. Ask: "What's my salary?"
4. Should work! 🎉

---

## 🐛 Troubleshooting

### **Error: No module named 'agents'**

**Fix:** Update the import in `hr_agent_sdk_new.py`:
```python
from openai import Agent, Runner, function_tool, RunContextWrapper
```

### **Error: Cannot import name 'Agent' from 'openai'**

**Fix:** Install separate agents-sdk:
```txt
# In requirements.txt, add:
agents-sdk>=1.0.0
```

### **Error: 'HRAgentSystem' object has no attribute 'chat' is not awaitable**

**Fix:** Make sure you're using Quart (async Flask), not regular Flask!

### **Still can't find employee**

Check Render logs for:
```
📊 First 5 Employee IDs: ['EID2480001', ...]
```

Then verify you're using an ID that exists!

---

## ✅ Expected Behavior

**Login with:** `EID2480002`

**Ask:** "What's my salary?"

**Logs show:**
```
📥 Question from employee EID2480002: What's my salary?
✅ Response: Your salary is $95,000.
```

**User sees:**
```
Your salary is $95,000.
```

---

## 🎯 Key Improvements

1. ✅ **Employee lookup actually works** - handles EID, numeric, and names
2. ✅ **Clean async code** - uses modern async/await
3. ✅ **Better debugging** - prints employee data on startup
4. ✅ **Proper error handling** - clear error messages
5. ✅ **Maintainable** - easy to add new tools

---

## 📊 Cost Estimate

Same as before:
- Model: `gpt-4o-mini`
- ~$1.40/month for 1000 employees × 10 questions each
- Super cost-effective! 💰

---

## 🚀 You're Ready!

Upload the files and deploy! The new system is **clean, modern, and actually works**! 🎉
