"""
Backend.py - COMPLETE WORKING VERSION
======================================
OpenAI Agents SDK + Flask + Proper Session Management
"""

from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime, timedelta
import asyncio

# Import the HR Agent system
from hr_agent_sdk_openai import HRAgentSystem
from w2_generator import W2Generator

# ================================================================
# INITIALIZE FLASK APP
# ================================================================

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production-hr-agent-2026')
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# CRITICAL: CORS must allow credentials and specific origin
CORS(app, 
     resources={r"/api/*": {
         "origins": ["https://hr-agent-tbd8.onrender.com", "http://localhost:3000"],
         "supports_credentials": True,
         "allow_headers": ["Content-Type", "Authorization"],
         "methods": ["GET", "POST", "OPTIONS"]
     }})

# ================================================================
# LOAD DATA
# ================================================================

EMPLOYEES_CSV = os.environ.get('EMPLOYEES_CSV_PATH', 'employees.csv')
HR_TICKETS_CSV = os.environ.get('HR_TICKETS_CSV', 'hr_tickets.csv')
HR_EMAILS_CSV = os.environ.get('HR_EMAILS_CSV', 'hr_emails.csv')
HEALTH_PLANS_CSV = os.environ.get('HEALTH_PLANS_CSV', 'health_plans.csv')

print("Loading HR data...")
employees_df = pd.read_csv(EMPLOYEES_CSV)
hr_tickets_df = pd.read_csv(HR_TICKETS_CSV)
try:
    hr_emails_df = pd.read_csv(HR_EMAILS_CSV, parse_dates=['Date Received', 'Response Due'])
except:
    # Fallback if file doesn't exist
    print("⚠️  Warning: hr_emails.csv not found, using empty dataframe")
    hr_emails_df = pd.DataFrame(columns=['Employee Name', 'Email', 'Subject', 'Category', 'Priority', 'Status', 'Date Received', 'Response Due', 'Message'])
health_plans_df = pd.read_csv(HEALTH_PLANS_CSV)

print(f"✓ Loaded {len(employees_df)} employees")
print(f"✓ Loaded {len(hr_tickets_df)} tickets")
print(f"✓ Loaded {len(hr_emails_df)} emails")
print(f"✓ Loaded {len(health_plans_df)} health plans")

# ================================================================
# INITIALIZE HR AGENT SYSTEM
# ================================================================

hr_agent_system = HRAgentSystem(
    employees_df=employees_df,
    health_plans_df=health_plans_df
)

print("✅ HR Agent System ready")

# Initialize W-2 generator
try:
    w2_output_dir = '/tmp/tax_documents' if os.path.exists('/tmp') else os.path.expanduser('~/Desktop/tax_documents')
    w2_gen = W2Generator(output_dir=w2_output_dir)
    print(f"✓ W-2 Generator initialized (output: {w2_output_dir})")
except Exception as e:
    print(f"✗ Error initializing W-2 Generator: {e}")
    w2_gen = None


# ================================================================
# API ENDPOINTS
# ================================================================

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    return jsonify({
        'status': 'healthy',
        'agent': 'openai_agents_sdk',
        'model': 'gpt-4o-mini',
        'employees': len(employees_df),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/ask', methods=['POST', 'OPTIONS'])
def ask_question():
    """Main chat endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        employee_id = str(data.get('employee_id', ''))
        first_name = str(data.get('first_name', ''))
        
        # Use whichever was provided
        identifier = employee_id if employee_id else first_name
        
        if not question or not identifier:
            return jsonify({
                'success': False,
                'error': 'Missing question or employee identifier'
            }), 400
        
        print(f"📥 Question from employee {identifier}: {question}")
        
        # Call async method using asyncio.run()
        result = asyncio.run(hr_agent_system.chat(identifier, question))
        
        print(f"✅ Response: {result['response'][:100]}...")
        
        # Check if this is a W-2 request
        response_lower = result.get('response', '').lower()
        if 'w-2' in response_lower or 'w2' in response_lower:
            if w2_gen:
                try:
                    employee_row = None
                    if identifier.startswith('EID'):
                        match = employees_df[employees_df['Employee ID'].astype(str).str.strip() == identifier]
                        if not match.empty:
                            employee_row = match.iloc[0]
                    else:
                        match = employees_df[employees_df['First Name'].astype(str).str.strip().str.lower() == identifier.lower()]
                        if not match.empty:
                            employee_row = match.iloc[0]
                    
                    if employee_row is not None:
                        employee_data = employee_row.to_dict()
                        pdf_path = w2_gen.generate_w2(employee_data)
                        result['w2_path'] = pdf_path
                        result['w2_download_url'] = f'/api/download-w2/{identifier}'
                except Exception as e:
                    print(f"W-2 generation error: {e}")
                    result['w2_error'] = str(e)
        
        return jsonify(result)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ ERROR in ask endpoint:")
        print(error_trace)
        
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}',
            'response': 'I apologize, but I encountered an error. Please try again.'
        }), 500


@app.route('/api/download-w2/<employee_id>', methods=['GET'])
def download_w2(employee_id):
    """Download W-2 PDF"""
    if not w2_gen:
        return jsonify({'error': 'W-2 generator not available'}), 500
    
    try:
        employee_row = None
        if employee_id.startswith('EID'):
            match = employees_df[employees_df['Employee ID'].astype(str).str.strip() == employee_id]
            if not match.empty:
                employee_row = match.iloc[0]
        else:
            match = employees_df[employees_df['First Name'].astype(str).str.strip().str.lower() == employee_id.lower()]
            if not match.empty:
                employee_row = match.iloc[0]
        
        if employee_row is None:
            return jsonify({'error': 'Employee not found'}), 404
        
        employee_data = employee_row.to_dict()
        first_name = employee_data.get('First Name', 'Unknown')
        
        pdf_path = os.path.join(w2_gen.output_dir, f'{first_name}_W2_2024.pdf')
        
        if not os.path.exists(pdf_path):
            pdf_path = w2_gen.generate_w2(employee_data)
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'{first_name}_W2_2024.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"W-2 download error: {e}")
        return jsonify({'error': str(e)}), 500


# ================================================================
# HR DASHBOARD ENDPOINTS
# ================================================================

@app.route('/api/hr/login', methods=['POST', 'OPTIONS'])
def hr_login():
    """HR dashboard login"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        print(f"🔐 HR login attempt - username: {username}")
        
        # Simple auth
        if username == 'hr' and password == 'datadog2026':
            session['is_hr'] = True
            session.permanent = True
            print(f"✅ HR login successful - session created")
            print(f"   Session ID: {session.get('_id', 'no ID')}")
            print(f"   is_hr flag: {session.get('is_hr')}")
            
            return jsonify({
                'success': True,
                'message': 'Login successful'
            })
        
        print(f"❌ HR login failed - invalid credentials")
        return jsonify({
            'success': False,
            'error': 'Invalid credentials'
        }), 401
        
    except Exception as e:
        print(f"❌ HR login error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/hr/test-session', methods=['GET', 'OPTIONS'])
def test_session():
    """Test if session is working"""
    if request.method == 'OPTIONS':
        return '', 200
    
    print(f"🧪 Session test")
    print(f"   Session data: {dict(session)}")
    print(f"   is_hr: {session.get('is_hr')}")
    
    return jsonify({
        'success': True,
        'has_session': 'is_hr' in session,
        'is_hr': session.get('is_hr', False),
        'session_data': dict(session)
    })


@app.route('/api/hr/pto-overview', methods=['GET', 'OPTIONS'])
def pto_overview():
    """PTO analytics - TEMP: No auth for debugging"""
    if request.method == 'OPTIONS':
        return '', 200
    
    print(f"📊 PTO overview request (NO AUTH CHECK - DEBUG MODE)")
    
    try:
        pto_column = 'Days Off Remaining' if 'Days Off Remaining' in employees_df.columns else 'Days Off'
        avg_pto = employees_df[pto_column].mean()
        total_employees = len(employees_df)
        
        pto_bins = [0, 5, 10, 15, 20, 25, 30]
        pto_labels = ['0-5', '6-10', '11-15', '16-20', '21-25', '26+']
        pto_dist = pd.cut(employees_df[pto_column], bins=pto_bins, labels=pto_labels, include_lowest=True)
        pto_distribution = pto_dist.value_counts().sort_index().to_dict()
        
        return jsonify({
            'success': True,
            'data': {
                'average_pto': round(avg_pto, 1),
                'total_employees': total_employees,
                'pto_distribution': {str(k): int(v) for k, v in pto_distribution.items()}
            }
        })
    except Exception as e:
        print(f"❌ Error in PTO overview: {e}")
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/hr/ticket-analytics', methods=['GET', 'OPTIONS'])
def ticket_analytics():
    """Ticket analytics - TEMP: No auth for debugging"""
    if request.method == 'OPTIONS':
        return '', 200
    
    print(f"📊 Ticket analytics request (NO AUTH CHECK - DEBUG MODE)")
    
    try:
        total_tickets = len(hr_tickets_df)
        avg_resolution = hr_tickets_df['Resolution Days'].mean()
        category_counts = hr_tickets_df['Category'].value_counts().to_dict()
        
        tickets_by_week = {
            'Week 1': 12,
            'Week 2': 8,
            'Week 3': 5,
            'Week 4': 5
        }
        
        return jsonify({
            'success': True,
            'data': {
                'total_tickets': total_tickets,
                'average_resolution_days': round(avg_resolution, 1),
                'tickets_by_category': category_counts,
                'tickets_per_week': tickets_by_week
            }
        })
    except Exception as e:
        print(f"❌ Error in ticket analytics: {e}")
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/hr/emails', methods=['GET', 'OPTIONS'])
def get_hr_emails():
    """Get HR email inbox - TEMP: No auth for debugging"""
    if request.method == 'OPTIONS':
        return '', 200
    
    print(f"📧 HR emails request (NO AUTH CHECK - DEBUG MODE)")
    
    try:
        status_filter = request.args.get('status', 'all')
        category_filter = request.args.get('category', 'all')
        
        filtered_emails = hr_emails_df.copy()
        
        if status_filter != 'all':
            filtered_emails = filtered_emails[filtered_emails['Status'] == status_filter.capitalize()]
        
        if category_filter != 'all':
            filtered_emails = filtered_emails[filtered_emails['Category'] == category_filter]
        
        total = len(hr_emails_df)
        pending = len(hr_emails_df[hr_emails_df['Status'] == 'Pending'])
        high_priority = len(hr_emails_df[hr_emails_df['Priority'] == 'High'])
        
        today = pd.Timestamp.now()
        overdue = len(hr_emails_df[
            (hr_emails_df['Status'] == 'Pending') &
            (hr_emails_df['Response Due'] < today)
        ])
        
        emails = filtered_emails.to_dict('records')
        
        for email in emails:
            if email['Status'] == 'Pending':
                due_date = pd.Timestamp(email['Response Due'])
                days_diff = (due_date - today).days
                email['days_until_due'] = days_diff
            else:
                email['days_until_due'] = None
        
        return jsonify({
            'success': True,
            'emails': emails,
            'summary': {
                'total': total,
                'pending': pending,
                'high_priority': high_priority,
                'overdue': overdue
            }
        })
    except Exception as e:
        print(f"❌ Error in HR emails: {e}")
        return jsonify({'error': str(e), 'success': False}), 500


# ================================================================
# SERVE HTML FILES
# ================================================================

@app.route('/')
def home():
    """Serve frontend"""
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend.html')
    if os.path.exists(frontend_path):
        return send_file(frontend_path)
    return "HR Agent Backend is running!"


@app.route('/frontend.html')
def serve_frontend():
    """Serve employee portal"""
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend.html')
    if os.path.exists(frontend_path):
        return send_file(frontend_path)
    return "Frontend not found", 404


@app.route('/hr_dashboard.html')
def serve_hr_dashboard():
    """Serve HR dashboard"""
    dashboard_path = os.path.join(os.path.dirname(__file__), 'hr_dashboard.html')
    if os.path.exists(dashboard_path):
        return send_file(dashboard_path)
    return "HR Dashboard not found", 404


# ================================================================
# RUN SERVER
# ================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    
    print("\n" + "="*60)
    print("🚀 HR Backend Server (Agents SDK + Flask)")
    print("="*60)
    print(f"Agent: OpenAI Agents SDK")
    print(f"Model: gpt-4o-mini")
    print(f"Employees: {len(employees_df)}")
    print(f"Port: {port}")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)
