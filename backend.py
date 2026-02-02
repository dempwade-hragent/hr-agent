"""
Flask Backend API for Dempsey's HR
Simple, working version
"""

from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
from hr_agent_sdk import HRAgent
from w2_generator import W2Generator
import os
import math
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pandas as pd
import json

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # For session management

# Enable CORS for ALL routes - this is critical!
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# IMPORTANT: Update this path to your CSV file
# For local development
CSV_PATH = os.getenv('CSV_PATH', "/Users/dempseywade/Desktop/Datadog/HRAgent/employees.csv")
TICKETS_PATH = os.getenv('TICKETS_PATH', "/Users/dempseywade/Desktop/Datadog/HRAgent/hr_tickets.csv")
HEALTH_PLANS_PATH = os.getenv('HEALTH_PLANS_PATH', "/Users/dempseywade/Desktop/Datadog/HRAgent/health_plans.csv")
HR_EMAILS_PATH = os.getenv('HR_EMAILS_PATH', "/Users/dempseywade/Desktop/Datadog/HRAgent/hr_emails.csv")

# For production, files will be in the same directory as backend.py
if not os.path.exists(CSV_PATH):
    CSV_PATH = os.path.join(os.path.dirname(__file__), 'employees.csv')
if not os.path.exists(TICKETS_PATH):
    TICKETS_PATH = os.path.join(os.path.dirname(__file__), 'hr_tickets.csv')
if not os.path.exists(HEALTH_PLANS_PATH):
    HEALTH_PLANS_PATH = os.path.join(os.path.dirname(__file__), 'health_plans.csv')
if not os.path.exists(HR_EMAILS_PATH):
    HR_EMAILS_PATH = os.path.join(os.path.dirname(__file__), 'hr_emails.csv')

# Initialize the HR Agent
try:
    agent = HRAgent(CSV_PATH, health_plans_df=None)  # Will be set after loading
    print(f"✓ HR Agent initialized successfully with {CSV_PATH}")
    print(f"✓ Loaded HR database with {len(agent.get_all_employees())} employees")
except Exception as e:
    print(f"✗ Error initializing HR Agent: {e}")
    agent = None

# Load HR Tickets Data
hr_tickets_df = None
try:
    if os.path.exists(TICKETS_PATH):
        hr_tickets_df = pd.read_csv(TICKETS_PATH)
        hr_tickets_df['Date Submitted'] = pd.to_datetime(hr_tickets_df['Date Submitted'])
        print(f"✓ HR Tickets loaded: {len(hr_tickets_df)} tickets")
    else:
        print(f"⚠️  HR tickets file not found: {TICKETS_PATH}")
except Exception as e:
    print(f"✗ Error loading tickets: {e}")

# Load Health Plans Data
health_plans_df = None
try:
    if os.path.exists(HEALTH_PLANS_PATH):
        health_plans_df = pd.read_csv(HEALTH_PLANS_PATH)
        if agent:
            agent.health_plans = health_plans_df  # Inject health plans into agent
        print(f"✓ Health Plans loaded: {len(health_plans_df)} plans")
    else:
        print(f"⚠️  Health plans file not found: {HEALTH_PLANS_PATH}")
except Exception as e:
    print(f"✗ Error loading health plans: {e}")

# Load HR Emails Data
hr_emails_df = None
try:
    if os.path.exists(HR_EMAILS_PATH):
        hr_emails_df = pd.read_csv(HR_EMAILS_PATH)
        hr_emails_df['Date Received'] = pd.to_datetime(hr_emails_df['Date Received'])
        hr_emails_df['Response Due'] = pd.to_datetime(hr_emails_df['Response Due'])
        print(f"✓ HR Emails loaded: {len(hr_emails_df)} emails")
    else:
        print(f"⚠️  HR emails file not found: {HR_EMAILS_PATH}")
except Exception as e:
    print(f"✗ Error loading HR emails: {e}")

# Initialize W-2 Generator
try:
    # Use environment variable or default to a temp directory in production
    w2_output_dir = os.getenv('W2_OUTPUT_DIR', '/tmp/tax_documents')
    
    # For local dev, use the desktop path
    local_path = "/Users/dempseywade/Desktop/Datadog/HRAgent/tax_documents"
    if os.path.exists(os.path.dirname(local_path)):
        w2_output_dir = local_path
    
    # Create directory if it doesn't exist
    os.makedirs(w2_output_dir, exist_ok=True)
    
    w2_gen = W2Generator(output_dir=w2_output_dir)
    print(f"✓ W-2 Generator initialized (output: {w2_output_dir})")
except Exception as e:
    print(f"✗ Error initializing W-2 Generator: {e}")
    w2_gen = None


@app.route('/')
def home():
    """Serve the frontend or redirect to it"""
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend.html')
    if os.path.exists(frontend_path):
        with open(frontend_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return """
        <html>
        <head><title>Dempsey's HR Backend</title></head>
        <body style="font-family: Arial; padding: 40px; max-width: 600px; margin: 0 auto;">
            <h1>🌿 Dempsey's HR Backend</h1>
            <p>The backend is running successfully!</p>
            <h2>Next Steps:</h2>
            <ol>
                <li>Make sure <code>frontend.html</code> is in the same folder as <code>backend.py</code></li>
                <li>Refresh this page</li>
                <li>Or open <a href="http://localhost:5000">http://localhost:5000</a> directly</li>
            </ol>
            <h2>API Endpoints:</h2>
            <ul>
                <li><a href="/api/health">/api/health</a> - Health check</li>
                <li>/api/ask - Ask questions (POST)</li>
                <li>/api/employees - List all employees</li>
            </ul>
        </body>
        </html>
        """


@app.route('/frontend.html')
def serve_frontend():
    """Serve frontend HTML"""
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend.html')
    if os.path.exists(frontend_path):
        return send_file(frontend_path)
    return "Frontend not found", 404


@app.route('/hr_dashboard.html')
def serve_hr_dashboard():
    """Serve HR dashboard - tries v2 first"""
    dashboard_v2_path = os.path.join(os.path.dirname(__file__), 'hr_dashboard_v2.html')
    dashboard_path = os.path.join(os.path.dirname(__file__), 'hr_dashboard.html')
    
    if os.path.exists(dashboard_v2_path):
        return send_file(dashboard_v2_path)
    elif os.path.exists(dashboard_path):
        return send_file(dashboard_path)
    return "HR Dashboard not found", 404


@app.route('/hr_dashboard_v2.html')
def serve_hr_dashboard_v2():
    """Serve HR dashboard v2"""
    dashboard_path = os.path.join(os.path.dirname(__file__), 'hr_dashboard_v2.html')
    if os.path.exists(dashboard_path):
        return send_file(dashboard_path)
    return "HR Dashboard v2 not found", 404


@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    return jsonify({
        'status': 'healthy',
        'agent_loaded': agent is not None,
        'message': 'Dempsey\'s HR backend is running!'
    })


@app.route('/api/ask', methods=['POST', 'OPTIONS'])
def ask_question():
    """Handle questions from the frontend"""
    print("\n" + "="*70)
    print("📨 RECEIVED REQUEST TO /api/ask")
    print("="*70)
    
    if request.method == 'OPTIONS':
        print("  Method: OPTIONS (preflight)")
        return '', 200
    
    print(f"  Method: {request.method}")
    print(f"  Headers: {dict(request.headers)}")
    
    if agent is None:
        print("  ❌ ERROR: Agent not initialized")
        return jsonify({
            'success': False,
            'error': 'HR Agent not initialized. Please check CSV file path.'
        }), 500
    
    try:
        data = request.get_json()
        print(f"  📦 Request data: {data}")
        
        if not data or 'question' not in data:
            print("  ❌ ERROR: No question in request")
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        question = data['question']
        employee_id = data.get('employee_id')
        first_name = data.get('first_name')
        
        print(f"  ❓ Question: {question}")
        print(f"  👤 Employee ID: {employee_id}")
        print(f"  👤 First Name: {first_name}")
        
        # Check if there's a pending location update and this is a remote response
        if 'pending_location_update' in session:
            pending = session['pending_location_update']
            
            # Check if this response is about remote status
            question_lower = question.lower().strip()
            is_remote_response = any([
                question_lower == 'remote',
                question_lower == 'remotely',
                'remote' in question_lower and len(question_lower) < 20,
                question_lower in ['onsite', 'on-site', 'on site', 'office'],
                'office' in question_lower and len(question_lower) < 20
            ])
            
            if is_remote_response:
                # Determine if remote or onsite
                is_remote = any(word in question_lower for word in ['remote'])
                
                # Get employee to find column names
                if employee_id:
                    employee = agent.database.get_employee_by_id(employee_id)
                else:
                    employee = agent.database.get_employee_by_name(first_name)
                
                if employee is not None:
                    location_col = 'Location' if 'Location' in employee.index else 'Town'
                    
                    # Prepare updates
                    updates = {location_col: pending['location']}
                    
                    # Add remote status if column exists
                    if 'On-site' in employee.index:
                        updates['On-site'] = 'No' if is_remote else 'Yes'
                    elif 'Remote' in employee.index:
                        updates['Remote'] = 'Yes' if is_remote else 'No'
                    
                    # Update the employee
                    success = agent.database.update_employee(
                        employee_id=employee_id,
                        first_name=first_name,
                        updates=updates
                    )
                    
                    # Clear the pending update
                    session.pop('pending_location_update', None)
                    
                    if success:
                        work_status = "remotely" if is_remote else "on-site"
                        print(f"  ✅ Updated location to {pending['location']} and status to {work_status}")
                        print("="*70 + "\n")
                        
                        return jsonify({
                            'success': True,
                            'answer': f"Perfect! I've updated your location to {pending['location']} and set your status to {work_status}.",
                            'intent': 'location_updated',
                            'raw_data': employee.to_dict()
                        })
        
        # Get answer from the agent
        result = agent.answer_question(
            question=question,
            employee_id=employee_id,
            first_name=first_name
        )
        
        print(f"  ✅ Answer: {result['answer']}")
        print(f"  🎯 Intent: {result['intent']}")
        
        # Fix NaN values in raw_data (do this FIRST before any checks)
        raw_data = result.get('raw_data', {})
        if raw_data:
            for key, value in raw_data.items():
                if isinstance(value, float) and math.isnan(value):
                    raw_data[key] = None
        
        # Check if this is a location update request (asking about remote)
        if result['answer'].startswith('LOCATION_UPDATE_REQUEST:'):
            new_location = result['answer'].split(':')[1]
            
            # Store in session
            session['pending_location_update'] = {
                'location': new_location,
                'employee_id': employee_id,
                'first_name': first_name
            }
            
            print("="*70 + "\n")
            
            return jsonify({
                'success': True,
                'answer': f"Great! I've noted that you're moving to {new_location}. Will you be working remotely from there, or relocating to an office?",
                'intent': 'location_update_pending',
                'raw_data': raw_data,
                'pending_update': {
                    'location': new_location,
                    'employee_id': employee_id,
                    'first_name': first_name
                }
            })
        
        # Check if this is a hybrid request (answer + needs HR approval)
        if result['answer'].startswith('HYBRID_REQUEST:'):
            user_question = result['answer'].split(':', 1)[1]
            
            # Get the actual answer by asking again with a modified question
            # that won't trigger the hybrid check
            info_result = agent.answer_question(
                question="Where do I work?",
                employee_id=employee_id,
                first_name=first_name
            )
            
            current_info = info_result['answer']
            
            # Get employee info for email context
            if employee_id:
                employee = agent.database.get_employee_by_id(employee_id)
            else:
                employee = agent.database.get_employee_by_name(first_name)
            
            if employee is not None:
                emp_name = employee.get('First Name', 'Unknown Employee')
                emp_id_val = employee.get('Employee ID') if 'Employee ID' in employee.index else employee.get('EmployeeID', 'N/A')
                
                # Draft the email
                subject = f"Policy Request from {emp_name} (ID: {emp_id_val})"
                
                body = f"""Dear HR Team,

{emp_name} (Employee ID: {emp_id_val}) has submitted the following request that requires policy review:

"{user_question}"

Current Status: {current_info}

This request was submitted via the HR Assistant system on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}.

Please review this policy request and respond to the employee at your earliest convenience.

Best regards,
Dempsey's HR Assistant System"""
                
                # Store email info in session
                session['pending_email'] = {
                    'employee_name': emp_name,
                    'employee_id': emp_id_val,
                    'question': user_question,
                    'subject': subject,
                    'body': body
                }
                
                print("="*70 + "\n")
                
                return jsonify({
                    'success': True,
                    'answer': f"{current_info}\n\nThis type of request typically requires HR approval. Would you like me to send a formal request to HR on your behalf?",
                    'intent': 'hybrid_request',
                    'raw_data': raw_data,
                    'email_draft': {
                        'to': 'demp.wade@gmail.com',
                        'subject': subject,
                        'body': body
                    }
                })
        
        # Check if this is an email HR request
        if result['answer'].startswith('EMAIL_HR_REQUEST:'):
            user_question = result['answer'].split(':', 1)[1]
            
            # Get employee info for context
            if employee_id:
                employee = agent.database.get_employee_by_id(employee_id)
            else:
                employee = agent.database.get_employee_by_name(first_name)
            
            if employee is not None:
                emp_name = employee.get('First Name', 'Unknown Employee')
                emp_id_val = employee.get('Employee ID') if 'Employee ID' in employee.index else employee.get('EmployeeID', 'N/A')
                
                # Draft the email immediately
                subject = f"HR Request from {emp_name} (ID: {emp_id_val})"
                
                body = f"""Dear HR Team,

{emp_name} (Employee ID: {emp_id_val}) has submitted the following request:

"{user_question}"

This request was submitted via the HR Assistant system on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}.

Please review and respond to the employee at your earliest convenience.

Best regards,
Dempsey's HR Assistant System"""
                
                # Store email info in session
                session['pending_email'] = {
                    'employee_name': emp_name,
                    'employee_id': emp_id_val,
                    'question': user_question,
                    'subject': subject,
                    'body': body
                }
                
                print("="*70 + "\n")
                
                return jsonify({
                    'success': True,
                    'answer': f"I've drafted this email to HR for you. Please review it and let me know if you'd like me to send it:",
                    'intent': 'email_hr_pending',
                    'raw_data': raw_data,
                    'email_draft': {
                        'to': 'demp.wade@gmail.com',
                        'subject': subject,
                        'body': body
                    }
                })
        
        # Check if this is an unknown question that should be sent to HR
        if result['answer'].startswith('EMAIL_HR_UNKNOWN:'):
            user_question = result['answer'].split(':', 1)[1]
            
            # Get employee info for context
            if employee_id:
                employee = agent.database.get_employee_by_id(employee_id)
            else:
                employee = agent.database.get_employee_by_name(first_name)
            
            if employee is not None:
                emp_name = employee.get('First Name', 'Unknown Employee')
                emp_id_val = employee.get('Employee ID') if 'Employee ID' in employee.index else employee.get('EmployeeID', 'N/A')
                
                # Draft the email immediately
                subject = f"HR Question from {emp_name} (ID: {emp_id_val})"
                
                body = f"""Dear HR Team,

{emp_name} (Employee ID: {emp_id_val}) has asked a question that requires HR expertise:

"{user_question}"

This question was submitted via the HR Assistant system on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}.

Please review and respond to the employee at your earliest convenience.

Best regards,
Dempsey's HR Assistant System"""
                
                # Store email info in session
                session['pending_email'] = {
                    'employee_name': emp_name,
                    'employee_id': emp_id_val,
                    'question': user_question,
                    'subject': subject,
                    'body': body
                }
                
                print("="*70 + "\n")
                
                return jsonify({
                    'success': True,
                    'answer': f"I'm not sure how to answer that question, but I can forward it to HR for you. Here's what I'll send:",
                    'intent': 'email_hr_unknown',
                    'raw_data': raw_data,
                    'email_draft': {
                        'to': 'demp.wade@gmail.com',
                        'subject': subject,
                        'body': body
                    }
                })
        
        # Check if this is a W-2 request
        if result['answer'].startswith('W2_REQUEST:'):
            first_name = result['answer'].split(':')[1]
            
            # Always regenerate W-2 with fresh data from the database
            # This ensures updates are reflected
            if employee_id:
                fresh_employee = agent.database.get_employee_by_id(employee_id)
            else:
                fresh_employee = agent.database.get_employee_by_name(first_name)
            
            if fresh_employee is not None:
                # Convert to dict and clean NaN values
                employee_data = fresh_employee.to_dict()
                for key, value in employee_data.items():
                    if isinstance(value, float) and math.isnan(value):
                        employee_data[key] = None
                
                # Generate W-2 (will overwrite if exists)
                w2_path = w2_gen.generate_w2(employee_data, 2024)
            
            # Return download link
            answer = f"I've prepared your 2024 W-2 form. You can download it below."
            download_url = f"/api/download/w2/{first_name}/2024"
            
            print("="*70 + "\n")
            
            return jsonify({
                'success': True,
                'answer': answer,
                'intent': result['intent'],
                'raw_data': raw_data,
                'download_url': download_url,
                'file_type': 'w2'
            })
        
        print("="*70 + "\n")
        
        return jsonify({
            'success': True,
            'answer': result['answer'],
            'intent': result['intent'],
            'raw_data': raw_data
        })
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("="*70 + "\n")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/employees', methods=['GET', 'OPTIONS'])
def get_employees():
    """Get list of all employees"""
    if request.method == 'OPTIONS':
        return '', 200
    
    if agent is None:
        return jsonify({
            'success': False,
            'error': 'HR Agent not initialized'
        }), 500
    
    try:
        employees = agent.get_all_employees()
        return jsonify({
            'success': True,
            'employees': employees[:10],  # Return first 10 for preview
            'count': len(employees)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/validate-employee', methods=['POST', 'OPTIONS'])
def validate_employee():
    """Validate if an employee exists"""
    if request.method == 'OPTIONS':
        return '', 200
    
    if agent is None:
        return jsonify({
            'success': False,
            'error': 'HR Agent not initialized'
        }), 500
    
    try:
        data = request.get_json()
        employee_id = data.get('employee_id')
        first_name = data.get('first_name')
        
        if employee_id:
            employee = agent.database.get_employee_by_id(employee_id)
        elif first_name:
            employee = agent.database.get_employee_by_name(first_name)
        else:
            return jsonify({
                'success': False,
                'error': 'Either employee_id or first_name is required'
            }), 400
        
        if employee is not None:
            return jsonify({
                'success': True,
                'valid': True,
                'name': employee['First Name']
            })
        else:
            return jsonify({
                'success': True,
                'valid': False,
                'error': 'Employee not found'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/download/w2/<first_name>/<int:year>', methods=['GET'])
def download_w2(first_name, year):
    """Download a W-2 PDF for an employee"""
    if w2_gen is None:
        return jsonify({
            'success': False,
            'error': 'W-2 generator not initialized'
        }), 500
    
    try:
        # Get W-2 path
        w2_path = w2_gen.get_w2_path(first_name, year)
        
        if not w2_path or not os.path.exists(w2_path):
            return jsonify({
                'success': False,
                'error': 'W-2 not found'
            }), 404
        
        # Send the file
        return send_file(
            w2_path,
            as_attachment=True,
            download_name=f"{first_name}_W2_{year}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/update', methods=['POST', 'OPTIONS'])
def update_employee():
    """Update employee information"""
    if request.method == 'OPTIONS':
        return '', 200
    
    if agent is None:
        return jsonify({
            'success': False,
            'error': 'HR Agent not initialized'
        }), 500
    
    try:
        data = request.get_json()
        
        employee_id = data.get('employee_id')
        first_name = data.get('first_name')
        field = data.get('field')
        new_value = data.get('value')
        
        if not field or not new_value:
            return jsonify({
                'success': False,
                'error': 'Field and value are required'
            }), 400
        
        result = agent.update_employee_data(
            employee_id=employee_id,
            first_name=first_name,
            field=field,
            new_value=new_value
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/update-location', methods=['POST', 'OPTIONS'])
def update_location_with_remote():
    """Complete a location update with remote status"""
    if request.method == 'OPTIONS':
        return '', 200
    
    if agent is None:
        return jsonify({
            'success': False,
            'error': 'HR Agent not initialized'
        }), 500
    
    try:
        data = request.get_json()
        
        location = data.get('location')
        is_remote = data.get('is_remote')
        employee_id = data.get('employee_id')
        first_name = data.get('first_name')
        
        if not location or is_remote is None:
            return jsonify({
                'success': False,
                'error': 'Location and remote status are required'
            }), 400
        
        # Determine column names
        if employee_id:
            employee = agent.database.get_employee_by_id(employee_id)
        else:
            employee = agent.database.get_employee_by_name(first_name)
        
        if employee is None:
            return jsonify({
                'success': False,
                'error': 'Employee not found'
            }), 404
        
        location_col = 'Location' if 'Location' in employee.index else 'Town'
        
        # Prepare updates
        updates = {location_col: location}
        
        # Add remote status if column exists
        if 'On-site' in employee.index:
            updates['On-site'] = 'No' if is_remote else 'Yes'
        elif 'Remote' in employee.index:
            updates['Remote'] = 'Yes' if is_remote else 'No'
        
        # Update the employee
        success = agent.database.update_employee(
            employee_id=employee_id,
            first_name=first_name,
            updates=updates
        )
        
        if success:
            work_status = "remotely" if is_remote else "on-site"
            return jsonify({
                'success': True,
                'answer': f"Perfect! I've updated your location to {location} and set your status to {work_status}."
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update location'
            }), 500
            
    except Exception as e:
        print(f"Error updating location: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/send-email-to-hr', methods=['POST', 'OPTIONS'])
def send_email_to_hr():
    """Send an email to HR with the employee's request"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if 'pending_email' not in session:
            return jsonify({
                'success': False,
                'error': 'No pending email found'
            }), 400
        
        pending = session['pending_email']
        subject = pending['subject']
        body = pending['body']
        
        # Try to send actual email via Gmail SMTP
        hr_email = 'demp.wade@gmail.com'
        email_sent = False
        
        try:
            # Note: For this to work in production, you need:
            # 1. Gmail App Password (not regular password)
            # 2. Set GMAIL_USER and GMAIL_APP_PASSWORD environment variables
            sender_email = os.environ.get('GMAIL_USER')
            sender_password = os.environ.get('GMAIL_APP_PASSWORD')
            
            if sender_email and sender_password:
                # Create message
                message = MIMEMultipart()
                message['From'] = sender_email
                message['To'] = hr_email
                message['Subject'] = subject
                message.attach(MIMEText(body, 'plain'))
                
                # Send via Gmail SMTP
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(sender_email, sender_password)
                    server.send_message(message)
                
                email_sent = True
                print(f"✅ EMAIL SENT to {hr_email}")
            else:
                print("⚠️  Gmail credentials not configured - email simulated only")
                print(f"   Set GMAIL_USER and GMAIL_APP_PASSWORD environment variables to enable")
        except Exception as smtp_error:
            print(f"⚠️  SMTP Error: {smtp_error}")
            print(f"   Email will be simulated")
        
        # Log the email details
        print(f"\n📧 EMAIL {'SENT' if email_sent else 'DRAFTED'}:")
        print(f"To: {hr_email}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print("="*70 + "\n")
        
        # Clear the pending email
        session.pop('pending_email', None)
        
        status_msg = "sent" if email_sent else "drafted (SMTP not configured - check server logs)"
        
        return jsonify({
            'success': True,
            'answer': f"Perfect! I've {status_msg} a professional email to HR ({hr_email}) with your request. They will review it and get back to you soon. Is there anything else I can help you with?",
            'email_sent': email_sent,
            'email_draft': {
                'to': hr_email,
                'subject': subject,
                'body': body
            }
        })
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Add after-request handler for CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


# HR Analytics Endpoints
@app.route('/api/hr/analytics/pto-usage', methods=['GET', 'OPTIONS'])
def get_pto_analytics():
    """Get PTO usage analytics"""
    if request.method == 'OPTIONS':
        return '', 200
    
    if agent is None:
        return jsonify({'success': False, 'error': 'HR Agent not initialized'}), 500
    
    try:
        df = agent.database.df
        
        # Calculate PTO statistics
        pto_data = {
            'average_days_remaining': float(df['Days Off Remaining'].mean()),
            'median_days_remaining': float(df['Days Off Remaining'].median()),
            'employees_low_pto': int(len(df[df['Days Off Remaining'] < 5])),
            'employees_high_pto': int(len(df[df['Days Off Remaining'] > 20])),
            'total_employees': len(df),
            'pto_distribution': df['Days Off Remaining'].value_counts().sort_index().head(30).to_dict()
        }
        
        return jsonify({'success': True, 'data': pto_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/hr/analytics/tickets', methods=['GET', 'OPTIONS'])
def get_ticket_analytics():
    """Get ticket analytics"""
    if request.method == 'OPTIONS':
        return '', 200
    
    if hr_tickets_df is None:
        return jsonify({'success': False, 'error': 'Tickets data not loaded'}), 500
    
    try:
        df = hr_tickets_df
        
        df['week'] = df['Date Submitted'].dt.to_period('W').astype(str)
        tickets_per_week = df.groupby('week').size().to_dict()
        
        tickets_by_category = df['Category'].value_counts().to_dict()
        
        resolved_df = df[df['Status'] == 'Resolved']
        avg_resolution_days = float(resolved_df['Resolution Days'].mean()) if len(resolved_df) > 0 else 0
        
        status_counts = df['Status'].value_counts().to_dict()
        
        analytics_data = {
            'tickets_per_week': tickets_per_week,
            'tickets_by_category': tickets_by_category,
            'average_resolution_days': avg_resolution_days,
            'status_counts': status_counts,
            'total_tickets': len(df),
            'pending_tickets': int(status_counts.get('Pending', 0))
        }
        
        return jsonify({'success': True, 'data': analytics_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/hr/emails', methods=['GET', 'OPTIONS'])
def get_hr_emails():
    """Get HR emails/requests from employees"""
    if request.method == 'OPTIONS':
        return '', 200
    
    if hr_emails_df is None:
        return jsonify({'success': False, 'error': 'HR emails data not loaded'}), 500
    
    try:
        # Get filter parameters
        status_filter = request.args.get('status', 'all')  # all, pending, resolved
        category_filter = request.args.get('category', 'all')
        
        df = hr_emails_df.copy()
        
        # Apply filters
        if status_filter != 'all':
            df = df[df['Status'].str.lower() == status_filter.lower()]
        
        if category_filter != 'all':
            df = df[df['Category'] == category_filter]
        
        # Convert to dict for JSON serialization
        emails = []
        for idx, row in df.iterrows():
            emails.append({
                'id': int(row['Email ID']),
                'employee_name': row['Employee Name'],
                'employee_id': int(row['Employee ID']),
                'subject': row['Subject'],
                'message': row['Message'],
                'category': row['Category'],
                'status': row['Status'],
                'priority': row['Priority'],
                'date_received': row['Date Received'].strftime('%Y-%m-%d'),
                'response_due': row['Response Due'].strftime('%Y-%m-%d'),
                'days_until_due': (row['Response Due'] - pd.Timestamp.now()).days
            })
        
        # Sort by priority and date
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        emails.sort(key=lambda x: (priority_order.get(x['priority'], 3), x['date_received']), reverse=True)
        
        # Get summary stats
        total_emails = len(hr_emails_df)
        pending_emails = len(hr_emails_df[hr_emails_df['Status'] == 'Pending'])
        high_priority = len(hr_emails_df[hr_emails_df['Priority'] == 'High'])
        overdue = len(hr_emails_df[hr_emails_df['Response Due'] < pd.Timestamp.now()])
        
        return jsonify({
            'success': True,
            'emails': emails,
            'summary': {
                'total': total_emails,
                'pending': pending_emails,
                'high_priority': high_priority,
                'overdue': overdue
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/hr/login', methods=['POST', 'OPTIONS'])
def hr_login():
    """HR login endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        username = data.get('username', '').lower()
        password = data.get('password', '')
        
        if username == 'hr' and password == 'datadog2026':
            session['is_hr'] = True
            return jsonify({
                'success': True,
                'message': 'HR login successful',
                'user_type': 'hr'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/hr_dashboard.html')
def serve_hr_dashboard():
    """Serve the HR dashboard HTML file"""
    # Try v2 first, then fall back to regular
    dashboard_v2_path = os.path.join(os.getcwd(), 'hr_dashboard_v2.html')
    dashboard_path = os.path.join(os.getcwd(), 'hr_dashboard.html')
    
    if os.path.exists(dashboard_v2_path):
        return send_file(dashboard_v2_path)
    elif os.path.exists(dashboard_path):
        return send_file(dashboard_path)
    else:
        return "HR Dashboard not found", 404


@app.route('/api/hr/check-auth', methods=['GET', 'OPTIONS'])
def check_hr_auth():
    """Check if user is authenticated as HR"""
    if request.method == 'OPTIONS':
        return '', 200
    
    is_hr = session.get('is_hr', False)
    return jsonify({'is_hr': is_hr})


@app.route('/')
def serve_frontend():
    """Serve the main frontend HTML file"""
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend.html')
    if os.path.exists(frontend_path):
        return send_file(frontend_path)
    else:
        return "Frontend not found", 404


@app.route('/frontend.html')
def serve_frontend_alt():
    """Alternative route for frontend"""
    return serve_frontend()


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌿 Dempsey's HR Backend Server")
    print("="*60)
    print(f"📊 CSV File: {CSV_PATH}")
    
    # Use PORT from environment variable (for cloud deployment) or default to 8080
    port = int(os.getenv('PORT', 8080))
    print(f"🌐 Server: http://localhost:{port}")
    print(f"💡 Open http://localhost:{port} in your browser!")
    print("="*60 + "\n")
    
    # For production, use 0.0.0.0 to accept external connections
    # For local dev, use 127.0.0.1
    host = '0.0.0.0' if os.getenv('PORT') else '127.0.0.1'
    
    app.run(debug=False if os.getenv('PORT') else True, port=port, host=host)
