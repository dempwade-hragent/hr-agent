"""
Backend.py - OpenAI Agents SDK Version
=======================================

CHANGES FROM ORIGINAL:
- Replaced hr_agent_sdk.py (regex) with hr_agent_sdk_openai.py (OpenAI Agents)
- Removed manual intent detection
- Agent automatically handles tool selection
- Stateful conversations via threads

All API endpoints remain the same for frontend compatibility!
"""

from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime

# CHANGED: Import OpenAI version instead of regex version
from hr_agent_sdk_openai import HRAgentOpenAI
from w2_generator import W2Generator

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'
CORS(app, supports_credentials=True)

# ================================================================
# LOAD DATA
# ================================================================

# Get CSV paths from environment or use defaults
EMPLOYEES_CSV = os.environ.get('EMPLOYEES_CSV_PATH', 'employees.csv')
HR_TICKETS_CSV = os.environ.get('HR_TICKETS_CSV', 'hr_tickets.csv')
HR_EMAILS_CSV = os.environ.get('HR_EMAILS_CSV', 'hr_emails.csv')
HEALTH_PLANS_CSV = os.environ.get('HEALTH_PLANS_CSV', 'health_plans.csv')

print("Loading HR data...")
employees_df = pd.read_csv(EMPLOYEES_CSV)
hr_tickets_df = pd.read_csv(HR_TICKETS_CSV)
hr_emails_df = pd.read_csv(HR_EMAILS_CSV, parse_dates=['Date Received', 'Response Due'])
health_plans_df = pd.read_csv(HEALTH_PLANS_CSV)

print(f"✓ Loaded {len(employees_df)} employees")
print(f"✓ Loaded {len(hr_tickets_df)} tickets")
print(f"✓ Loaded {len(hr_emails_df)} emails")
print(f"✓ Loaded {len(health_plans_df)} health plans")

# ================================================================
# INITIALIZE OPENAI AGENT (Replaces old regex agent)
# ================================================================

# CHANGED: Use OpenAI Agents SDK instead of regex
agent = HRAgentOpenAI(
    employees_df=employees_df,
    health_plans_df=health_plans_df
)

print(f"✅ OpenAI HR Agent initialized")

# Initialize W-2 generator
try:
    w2_output_dir = '/tmp/tax_documents' if os.path.exists('/tmp') else os.path.expanduser('~/Desktop/tax_documents')
    w2_gen = W2Generator(employees_df, output_dir=w2_output_dir)
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
        'agent': 'openai_agents_sdk',  # CHANGED: Now using OpenAI
        'model': 'gpt-4o-mini',
        'employees': len(employees_df),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/ask', methods=['POST', 'OPTIONS'])
def ask_question():
    """
    Main chat endpoint
    
    CHANGED: Now uses OpenAI Agents SDK instead of regex
    Agent automatically:
    - Detects intent (no regex needed!)
    - Calls appropriate tools
    - Formats response
    """
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json
        question = data.get('question', '').strip()
        employee_id = str(data.get('employee_id', ''))
        
        if not question or not employee_id:
            return jsonify({
                'success': False,
                'error': 'Missing question or employee_id'
            }), 400
        
        # Get session ID for conversation continuity
        session_id = session.get('session_id', employee_id)
        session['session_id'] = session_id
        
        # CHANGED: Let OpenAI agent handle everything!
        # No more regex, no more if/else chains
        result = agent.chat(
            employee_id=employee_id,
            message=question,
            session_id=session_id
        )
        
        # Check if this is a W-2 request
        if 'w2_generation' in str(result):
            if w2_gen:
                try:
                    pdf_path = w2_gen.generate_w2(int(employee_id))
                    result['w2_path'] = pdf_path
                    result['w2_download_url'] = f'/api/download-w2/{employee_id}'
                except Exception as e:
                    result['w2_error'] = str(e)
        
        # Check if this is an HR escalation
        if 'email_hr' in str(result):
            result['escalated'] = True
            result['action'] = 'email_drafted'
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error in ask endpoint: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'response': 'I apologize, but I encountered an error. Please try again.'
        }), 500


@app.route('/api/download-w2/<employee_id>', methods=['GET'])
def download_w2(employee_id):
    """Download W-2 PDF"""
    if not w2_gen:
        return jsonify({'error': 'W-2 generator not available'}), 500
    
    try:
        pdf_path = os.path.join(w2_gen.output_dir, f'W2_2024_Employee_{employee_id}.pdf')
        
        if not os.path.exists(pdf_path):
            # Generate if doesn't exist
            pdf_path = w2_gen.generate_w2(int(employee_id))
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'W2_2024_Employee_{employee_id}.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/employees', methods=['GET'])
def list_employees():
    """Get all employees (for testing)"""
    return jsonify({
        'success': True,
        'count': len(employees_df),
        'employees': employees_df.head(10).to_dict('records')
    })


@app.route('/api/hr/login', methods=['POST', 'OPTIONS'])
def hr_login():
    """HR dashboard login"""
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Simple auth (use proper auth in production!)
    if username == 'hr' and password == 'datadog2026':
        session['is_hr'] = True
        return jsonify({
            'success': True,
            'message': 'Login successful'
        })
    
    return jsonify({
        'success': False,
        'error': 'Invalid credentials'
    }), 401


@app.route('/api/hr/pto-overview', methods=['GET'])
def pto_overview():
    """PTO analytics for HR dashboard"""
    if not session.get('is_hr'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    avg_pto = employees_df['Days Off'].mean()
    total_employees = len(employees_df)
    
    # PTO distribution
    pto_bins = [0, 5, 10, 15, 20, 25, 30]
    pto_labels = ['0-5', '6-10', '11-15', '16-20', '21-25', '26+']
    pto_dist = pd.cut(employees_df['Days Off'], bins=pto_bins, labels=pto_labels, include_lowest=True)
    pto_distribution = pto_dist.value_counts().sort_index().to_dict()
    
    return jsonify({
        'success': True,
        'data': {
            'average_pto': round(avg_pto, 1),
            'total_employees': total_employees,
            'pto_distribution': {str(k): int(v) for k, v in pto_distribution.items()}
        }
    })


@app.route('/api/hr/ticket-analytics', methods=['GET'])
def ticket_analytics():
    """Ticket analytics for HR dashboard"""
    if not session.get('is_hr'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    total_tickets = len(hr_tickets_df)
    avg_resolution = hr_tickets_df['Resolution Days'].mean()
    
    # Tickets by category
    category_counts = hr_tickets_df['Category'].value_counts().to_dict()
    
    # Tickets per week (simplified)
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


@app.route('/api/hr/emails', methods=['GET'])
def get_hr_emails():
    """Get HR email inbox"""
    if not session.get('is_hr'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Filter parameters
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category', 'all')
    
    filtered_emails = hr_emails_df.copy()
    
    if status_filter != 'all':
        filtered_emails = filtered_emails[filtered_emails['Status'] == status_filter.capitalize()]
    
    if category_filter != 'all':
        filtered_emails = filtered_emails[filtered_emails['Category'] == category_filter]
    
    # Calculate stats
    total = len(hr_emails_df)
    pending = len(hr_emails_df[hr_emails_df['Status'] == 'Pending'])
    high_priority = len(hr_emails_df[hr_emails_df['Priority'] == 'High'])
    
    # Overdue count
    today = pd.Timestamp.now()
    overdue = len(hr_emails_df[
        (hr_emails_df['Status'] == 'Pending') &
        (hr_emails_df['Response Due'] < today)
    ])
    
    # Convert to records
    emails = filtered_emails.to_dict('records')
    
    # Calculate days until due for each email
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


@app.route('/')
def home():
    """Serve frontend"""
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend.html')
    if os.path.exists(frontend_path):
        return send_file(frontend_path)
    return "HR Agent Backend is running! Use /frontend.html or /hr_dashboard.html"


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
# CLEANUP ON SHUTDOWN
# ================================================================

import atexit

def cleanup():
    """Clean up OpenAI resources"""
    try:
        agent.cleanup()
    except:
        pass

atexit.register(cleanup)


# ================================================================
# RUN SERVER
# ================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    
    print("\n" + "="*60)
    print("🌿 HR Backend Server (OpenAI Agents SDK)")
    print("="*60)
    print(f"Agent: OpenAI Assistants API")
    print(f"Model: gpt-4o-mini")
    print(f"Employees: {len(employees_df)}")
    print(f"Port: {port}")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)
