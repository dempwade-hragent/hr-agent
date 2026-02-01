# Email Setup Guide

Your HR Agent can now send **real emails** to HR! Here's how to set it up:

## 📧 Gmail SMTP Setup

### Step 1: Create a Gmail App Password

1. Go to your **Google Account** (https://myaccount.google.com/)
2. Click **Security** in the left sidebar
3. Under "How you sign in to Google," click **2-Step Verification** (you must have this enabled)
4. Scroll down and click **App passwords**
5. Select **Mail** as the app
6. Select **Mac** or **Windows Computer** as the device
7. Click **Generate**
8. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

### Step 2: Set Environment Variables

**On Mac/Linux:**
```bash
export GMAIL_USER="your.email@gmail.com"
export GMAIL_APP_PASSWORD="abcd efgh ijkl mnop"
```

**On Windows (PowerShell):**
```powershell
$env:GMAIL_USER="your.email@gmail.com"
$env:GMAIL_APP_PASSWORD="abcd efgh ijkl mnop"
```

**Or add to your `~/.bash_profile` or `~/.zshrc` for persistence:**
```bash
export GMAIL_USER="your.email@gmail.com"
export GMAIL_APP_PASSWORD="abcd efgh ijkl mnop"
```

### Step 3: Restart the Backend

```bash
python3 backend.py
```

## ✅ How It Works

### Without SMTP Configuration:
- Email is **drafted and logged** to the terminal
- User sees the draft but email is not actually sent
- Backend logs show: `⚠️  Gmail credentials not configured - email simulated only`

### With SMTP Configuration:
- Email is **actually sent** via Gmail SMTP
- User receives confirmation: `Perfect! I've sent a professional email to HR`
- Backend logs show: `✅ EMAIL SENT to demp.wade@gmail.com`

## 🔒 Security Notes

- **Never commit** your App Password to git
- Use environment variables or a `.env` file
- App Passwords are specific to one application
- You can revoke them anytime in Google Account settings

## 📝 Email Format

Emails are sent in this format:

```
To: demp.wade@gmail.com
Subject: HR Request from KobeBean (ID: 12345)

Dear HR Team,

KobeBean (Employee ID: 12345) has submitted the following request:

"Is there a way I can take an extra day off?"

This request was submitted via the HR Assistant system on 
January 30, 2026 at 01:24 PM.

Please review and respond to the employee at your earliest convenience.

Best regards,
Dempsey's HR Assistant System
```

## 🧪 Testing

1. Ask the agent: `"Can I take an extra day off?"`
2. Review the email draft shown
3. Click **Send Email**
4. Check the terminal logs
5. Check demp.wade@gmail.com inbox if SMTP is configured

## 🎯 Troubleshooting

**Email not sending?**
- Check environment variables are set: `echo $GMAIL_USER`
- Ensure 2-Step Verification is enabled on Google Account
- Verify App Password (not regular password)
- Check terminal logs for error messages

**Still not working?**
- Try generating a new App Password
- Make sure you're using Gmail (not other email providers)
- Check firewall settings aren't blocking port 465

## 🔄 Alternative Email Services

To use a different email service, modify the SMTP settings in `backend.py`:

```python
# For Outlook/Office365:
with smtplib.SMTP_SSL('smtp.office365.com', 587) as server:
    ...

# For custom SMTP:
with smtplib.SMTP_SSL('smtp.yourdomain.com', 465) as server:
    ...
```
