# 🆕 NEW FEATURES GUIDE

Dempsey's HR now has TWO powerful new features:

## 📄 Feature 1: W-2 Tax Document Generation

Employees can now request and download their W-2 forms!

### How to Use:

**Ask questions like:**
- "Can I get my W-2?"
- "Show me my W-2 form"
- "I need my tax documents"
- "Download my W-2"

**What happens:**
1. The system generates a realistic W-2 PDF with:
   - Employee information
   - Wages and salary
   - Federal, Social Security, and Medicare taxes
   - State taxes
   - Professional formatting

2. A download button appears in the chat
3. Click to download: `{FirstName}_W2_2024.pdf`

**Example:**
```
You: Can I get my W-2?
Bot: I've prepared your 2024 W-2 form. You can download it below.
     [📄 Download W-2] ← Click this button
```

---

## ✏️ Feature 2: Editable Database

You can now UPDATE your employee information in real-time!

### How to Use:

**Ask to update information:**
- "Change my address to Boston"
- "Update my town to Seattle"
- "Change my team to Engineering"

**Supported updates:**
- **Address/Town/City** → Updates your location
- **Salary** → Updates your salary (for testing)
- **Bonus** → Updates bonus percentage
- **Days Off/PTO** → Updates remaining vacation days
- **Team** → Updates team assignment

**What happens:**
1. The system updates the CSV file
2. Changes are saved permanently
3. Next time you ask, you'll see the new data

**Example:**
```
You: Change my address to New York
Bot: Successfully updated address to New York.

You: What's my address?
Bot: Thomas works on-site in New York.
```

---

## 🚀 Installation

### Step 1: Install New Dependencies

```bash
pip install reportlab
```

Or install everything:
```bash
pip install -r requirements.txt
```

### Step 2: Add W-2 Generator

Copy `w2_generator.py` to `/Users/dempseywade/Desktop/Datadog/HRAgent/`

### Step 3: Update Files

Replace these files in your HRAgent folder:
- `backend.py` (updated with W-2 and update endpoints)
- `hr_agent_sdk.py` (updated with database update methods)
- `frontend.html` (updated to show download buttons)

### Step 4: Restart Backend

```bash
cd /Users/dempseywade/Desktop/Datadog/HRAgent
python3 backend.py
```

### Step 5: Test!

Go to `http://localhost:8080` and try:
- "Can I get my W-2?"
- "Change my address to Miami"

---

## 📁 File Structure

```
HRAgent/
├── employees.csv              (your employee database - now UPDATABLE!)
├── backend.py                 (updated with new endpoints)
├── hr_agent_sdk.py           (updated with update methods)
├── frontend.html              (updated with download buttons)
├── w2_generator.py           (NEW - generates W-2 PDFs)
└── tax_documents/            (NEW - auto-created, stores W-2s)
    ├── Thomas_W2_2024.pdf
    ├── Sarah_W2_2024.pdf
    └── ...
```

---

## 🎨 How It Works

### W-2 Generation:

1. Employee asks for W-2
2. SDK detects "w2" intent
3. Backend calls W2Generator
4. PDF created with employee data from CSV
5. File saved to `tax_documents/` folder
6. Download link returned to frontend
7. Button appears in chat

### Database Updates:

1. Employee asks to change something
2. SDK detects "update_info" intent
3. Backend calls `agent.update_employee_data()`
4. CSV file is updated
5. Confirmation message sent back

---

## 🧪 Testing

### Test W-2 Download:

```
You: Can I get my W-2?
Expected: Download button appears
Click: Downloads Thomas_W2_2024.pdf
```

### Test Database Update:

```
You: Change my town to Boston
Expected: "Successfully updated town to Boston."

You: Where do I work?
Expected: "Thomas works on-site in Boston."

Check: Open employees.csv - Thomas's Town should be "Boston"
```

---

## 🛠️ Customization

### Change W-2 Tax Calculations:

Edit `w2_generator.py` lines 95-98:
```python
federal_tax = wages * 0.22      # 22% federal
social_security = wages * 0.062  # 6.2% SS
medicare = wages * 0.0145        # 1.45% medicare
state_tax = wages * 0.05         # 5% state
```

### Add More Updatable Fields:

Edit `hr_agent_sdk.py` in the `update_employee_data` method:
```python
field_mapping = {
    'phone': 'Phone Number',    # Add phone updates
    'email': 'Email',           # Add email updates
    # etc.
}
```

### Change W-2 Year:

When asking, specify year:
```
"Can I get my 2023 W-2?"
```

Or edit backend default year.

---

## ⚠️ Important Notes

### Security Considerations:

1. **W-2s contain sensitive data** - In production:
   - Add authentication
   - Encrypt PDFs
   - Limit access by employee ID

2. **Database updates are permanent** - In production:
   - Add permissions (who can update what)
   - Add audit logging
   - Require manager approval

3. **This is a demo** - The W-2s have:
   - "SAMPLE" watermark
   - Simplified tax calculations
   - Disclaimer at bottom

### File Permissions:

Make sure the backend can write to:
- `/Users/dempseywade/Desktop/Datadog/HRAgent/tax_documents/`
- `/Users/dempseywade/Desktop/Datadog/HRAgent/employees.csv`

---

## 🎉 You're All Set!

Your HR system now has:
- ✅ Natural language Q&A
- ✅ W-2 document generation & download
- ✅ Real-time database updates
- ✅ Beautiful serene interface

Enjoy your enhanced Dempsey's HR! 🌿✨
