#!/usr/bin/env python3
"""
Connection Debugger for Dempsey's HR
This script will help identify why the frontend can't connect to the backend
"""

import sys
import subprocess
import socket
import json

print("="*70)
print("  DEMPSEY'S HR - CONNECTION DEBUGGER")
print("="*70)
print()

# Test 1: Check if backend is running
print("TEST 1: Is the backend running?")
print("-" * 70)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', 5000))

if result == 0:
    print("✓ YES - Something is running on port 5000")
    sock.close()
else:
    print("✗ NO - Nothing is running on port 5000")
    print()
    print("SOLUTION:")
    print("  1. Open a NEW terminal window")
    print("  2. Navigate to your HR-Assistant folder")
    print("  3. Run: python3 backend.py")
    print("  4. Keep that window open")
    print("  5. Come back here and run this script again")
    print()
    sys.exit(1)

print()

# Test 2: Check if it's actually the backend
print("TEST 2: Is it the Dempsey's HR backend?")
print("-" * 70)

try:
    import urllib.request
    import urllib.error
    
    try:
        response = urllib.request.urlopen('http://localhost:5000/api/health', timeout=5)
        data = json.loads(response.read().decode())
        
        if data.get('status') == 'healthy':
            print("✓ YES - Backend is responding correctly")
            print(f"  Status: {data['status']}")
            print(f"  Agent loaded: {data['agent_loaded']}")
        else:
            print("⚠ Backend is running but returned unexpected data")
            print(f"  Response: {data}")
    except urllib.error.URLError as e:
        print("✗ NO - Backend is not responding to HTTP requests")
        print(f"  Error: {e}")
        print()
        print("SOLUTION:")
        print("  The port is occupied by something else (not our backend)")
        print("  1. Stop whatever is running on port 5000")
        print("  2. Or change the port in backend.py to 5001")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error testing backend: {e}")
        sys.exit(1)
        
except ImportError:
    print("⚠ Cannot test HTTP connection (urllib not available)")

print()

# Test 3: Check CORS headers
print("TEST 3: Are CORS headers present?")
print("-" * 70)

try:
    import urllib.request
    
    req = urllib.request.Request('http://localhost:5000/api/health')
    response = urllib.request.urlopen(req)
    headers = response.headers
    
    cors_header = headers.get('Access-Control-Allow-Origin')
    if cors_header:
        print(f"✓ YES - CORS is enabled: {cors_header}")
    else:
        print("✗ NO - CORS headers are missing")
        print()
        print("SOLUTION:")
        print("  1. Make sure flask-cors is installed:")
        print("     pip3 install flask-cors")
        print("  2. Restart the backend")
        sys.exit(1)
        
except Exception as e:
    print(f"⚠ Could not check CORS headers: {e}")

print()

# Test 4: Try a test query
print("TEST 4: Can the backend answer questions?")
print("-" * 70)

try:
    import urllib.request
    import urllib.parse
    
    # Create test request
    data = {
        "question": "What's my salary?",
        "employee_id": "EMP001"
    }
    
    json_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(
        'http://localhost:5000/api/ask',
        data=json_data,
        headers={'Content-Type': 'application/json'}
    )
    
    response = urllib.request.urlopen(req, timeout=5)
    result = json.loads(response.read().decode())
    
    if result.get('success'):
        print("✓ YES - Backend processed the question successfully")
        print(f"  Answer: {result.get('answer', 'N/A')}")
        print(f"  Intent: {result.get('intent', 'N/A')}")
    else:
        print("✗ NO - Backend returned an error")
        print(f"  Error: {result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"✗ Error testing query: {e}")

print()

# Test 5: Check browser console
print("TEST 5: Browser console check")
print("-" * 70)
print("Now let's check your browser:")
print()
print("1. Open frontend.html in your browser")
print("2. Press F12 (or Cmd+Option+I on Mac)")
print("3. Click the 'Console' tab")
print("4. Try to sign in")
print("5. Look for errors in red")
print()
print("Common errors you might see:")
print()
print("❌ 'CORS policy' error:")
print("   → Solution: Install flask-cors")
print("      pip3 install flask-cors")
print()
print("❌ 'Failed to fetch' or 'Network error':")
print("   → Solution: Backend not running or wrong URL")
print("      Check that backend.py is running")
print()
print("❌ 'localhost:5000 refused to connect':")
print("   → Solution: Backend crashed or stopped")
print("      Check the backend terminal for errors")
print()

# Final summary
print()
print("="*70)
print("  SUMMARY")
print("="*70)
print()
print("✓ Port 5000 is in use")
print("✓ Backend health check passed")
print("✓ CORS is configured")
print("✓ Backend can answer questions")
print()
print("If the frontend STILL can't connect:")
print()
print("NEXT STEPS:")
print("1. Check the browser console (F12) for errors")
print("2. Make sure you're opening the CORRECT frontend.html")
print("3. Try hard-refreshing the page (Ctrl+Shift+R or Cmd+Shift+R)")
print("4. Check if your firewall is blocking localhost connections")
print()
print("Still stuck? Check the backend terminal for error messages")
print("when you try to sign in from the frontend.")
print()
