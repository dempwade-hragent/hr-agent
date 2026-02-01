#!/usr/bin/env python3
"""
Simple Backend Tester
Run this WHILE the backend is running to test if it works
"""

import urllib.request
import urllib.error
import json
import sys

print("="*60)
print("  TESTING BACKEND CONNECTION")
print("="*60)
print()

# Test the health endpoint
print("Testing: http://localhost:5000/api/health")
print()

try:
    response = urllib.request.urlopen('http://localhost:5000/api/health', timeout=5)
    data = json.loads(response.read().decode())
    
    print("✓ SUCCESS! Backend is responding")
    print(f"  Status: {data.get('status')}")
    print(f"  Agent loaded: {data.get('agent_loaded')}")
    print()
    
except urllib.error.URLError as e:
    print("✗ FAILED - Cannot connect to backend")
    print(f"  Error: {e}")
    print()
    print("Make sure backend.py is running!")
    print("Run in another terminal: python3 backend.py")
    sys.exit(1)

# Test asking a question
print("Testing: Asking a sample question...")
print()

try:
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
        print("✓ SUCCESS! Backend answered the question")
        print(f"  Question: {data['question']}")
        print(f"  Answer: {result['answer']}")
        print(f"  Intent: {result['intent']}")
    else:
        print("✗ Backend returned an error:")
        print(f"  {result.get('error')}")
        
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print()
print("="*60)
print("✅ BACKEND IS WORKING CORRECTLY!")
print("="*60)
print()
print("The backend is running fine. If the frontend still")
print("can't connect, the issue is likely:")
print()
print("1. Browser cache - Try hard refresh (Ctrl+Shift+R)")
print("2. Wrong frontend.html file - Make sure it's the updated one")
print("3. Browser security settings blocking localhost")
print()
print("Check the browser console (F12) for error messages.")
print()
