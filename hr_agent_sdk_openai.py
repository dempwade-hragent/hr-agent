"""
HR Agent - STANDARD OPENAI FUNCTION CALLING
==========================================
No SDK nonsense - just standard OpenAI API that actually works
"""

from openai import OpenAI
import pandas as pd
import json
from typing import Optional

client = OpenAI()

# ================================================================
# HELPER FUNCTIONS
# ================================================================

def find_employee(employees_df: pd.DataFrame, employee_id: str) -> Optional[dict]:
    """Find employee by ID or first name"""
    
    # Try by Employee ID
    if employee_id.upper().startswith('EID'):
        match = employees_df[employees_df['Employee ID'].astype(str).str.strip().str.upper() == employee_id.upper()]
        if not match.empty:
            return match.iloc[0].to_dict()
    
    # Try by first name
    match = employees_df[employees_df['First Name'].astype(str).str.strip().str.lower() == employee_id.lower()]
    if not match.empty:
        return match.iloc[0].to_dict()
    
    return None


# ================================================================
# FUNCTION DEFINITIONS FOR OPENAI
# ================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_employee_salary",
            "description": "Get employee's salary information",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "Employee ID or first name"}
                },
                "required": ["employee_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pto_balance",
            "description": "Get employee's PTO/vacation days remaining",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "Employee ID or first name"}
                },
                "required": ["employee_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_health_insurance_plans",
            "description": "Get available health insurance plans",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_hr",
            "description": "Escalate a request to HR (for enrollment, raises, benefits changes, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "Employee ID or first name"},
                    "subject": {"type": "string", "description": "Email subject line"},
                    "reason": {"type": "string", "description": "Detailed reason for escalation"}
                },
                "required": ["employee_id", "subject", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "email_manager",
            "description": "Draft an email to the employee's manager (for PTO requests, questions, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "Employee ID or first name"},
                    "subject": {"type": "string", "description": "Email subject line"},
                    "message": {"type": "string", "description": "Email message content"}
                },
                "required": ["employee_id", "subject", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_hr_meeting",
            "description": "Schedule a meeting with HR",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "Employee ID or first name"},
                    "reason": {"type": "string", "description": "Reason for the meeting"}
                },
                "required": ["employee_id", "reason"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a helpful HR assistant. Answer questions directly and use tools when needed.

CRITICAL RULE - REMEMBER YOUR OFFERS:
If you JUST said "Would you like me to X?" and user says "yes/sure/okay"
→ DO X IMMEDIATELY. Don't ask what they want.

EXAMPLES:

EXAMPLE 1 - PTO REQUEST (EXACT SCENARIO):
User: "Can I take a day off on Monday?"
You: [Call get_pto_balance]
You: "You have 13 PTO days remaining. To request time off, I can help you email your manager for approval. Would you like me to do that?"
User: "Yes"
You: [IMMEDIATELY call email_manager with subject="PTO Request for Monday" and message about Monday]
You: "Here's the email draft: [show email_draft from JSON]"

WRONG BEHAVIOR (NEVER DO THIS):
User: "Yes"
You: "What can I assist you with today?" ← FORBIDDEN! You JUST offered to email manager!

EXAMPLE 2 - 401K ENROLLMENT:
User: "What are my 401k options?"
You: "Company offers 401(k) with matching. Would you like to enroll?"
User: "Yes I'd like to enroll"
You: [IMMEDIATELY call escalate_to_hr with subject="401(k) Enrollment Request"]
You: "Here's the email to HR: [show email_draft]"

WRONG BEHAVIOR (NEVER DO THIS):
User: "Yes I'd like to enroll"
You: "What would you like to enroll in?" ← FORBIDDEN! You were JUST talking about 401k!

SIMPLE RULES:
1. Answer questions directly
2. Use tools to get data (salary, PTO, health plans)
3. When user wants to DO something (enroll, take PTO, etc.), use email_manager or escalate_to_hr
4. Always show the email_draft from tool responses
5. When user says "yes" to your offer, DO IT - don't ask again

BE DIRECT. CALL TOOLS. REMEMBER CONTEXT."""


# ================================================================
# TOOL EXECUTION
# ================================================================

def execute_function(function_name: str, arguments: dict, employees_df: pd.DataFrame, health_plans_df: pd.DataFrame) -> str:
    """Execute a function call and return the result"""
    
    print(f"\n🔧 EXECUTING: {function_name}({arguments})")
    
    if function_name == "get_employee_salary":
        employee = find_employee(employees_df, arguments['employee_id'])
        if employee is None:
            return json.dumps({'success': False, 'error': 'Employee not found'})
        return json.dumps({'success': True, 'salary': employee.get('Salary', 'Unknown')})
    
    elif function_name == "get_pto_balance":
        employee = find_employee(employees_df, arguments['employee_id'])
        if employee is None:
            return json.dumps({'success': False, 'error': 'Employee not found'})
        pto_column = 'Days Off Remaining' if 'Days Off Remaining' in employees_df.columns else 'Days Off'
        return json.dumps({'success': True, 'pto_remaining': employee.get(pto_column, 'Unknown')})
    
    elif function_name == "get_health_insurance_plans":
        plans = []
        for _, plan in health_plans_df.iterrows():
            plans.append({
                'name': plan['Plan Name'],
                'type': plan['Plan Type'],
                'employee_cost': plan['Employee Monthly Cost'],
                'family_cost': plan['Family Monthly Cost'],
                'deductible': plan['Deductible']
            })
        return json.dumps({'success': True, 'plans': plans})
    
    elif function_name == "escalate_to_hr":
        employee = find_employee(employees_df, arguments['employee_id'])
        name = 'Unknown Employee'
        emp_id_display = arguments['employee_id']
        if employee is not None:
            name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
            emp_id_display = employee.get('Employee ID', arguments['employee_id'])
        
        email_body = f"""Dear HR Team,

Employee: {name} (ID: {emp_id_display})
Subject: {arguments['subject']}

REQUEST DETAILS:
{arguments['reason']}

This request has been escalated for your review and assistance.

Best regards,
HR Assistant Bot"""
        
        return json.dumps({
            'success': True,
            'action': 'escalate_to_hr',
            'employee_id': arguments['employee_id'],
            'name': name,
            'subject': arguments['subject'],
            'reason': arguments['reason'],
            'email_draft': email_body,
            'recipient': 'hr@company.com'
        })
    
    elif function_name == "email_manager":
        employee = find_employee(employees_df, arguments['employee_id'])
        if employee is None:
            return json.dumps({'success': False, 'error': 'Employee not found'})
        
        employee_name = employee.get('First Name', 'Unknown')
        manager_name = employee.get('Manager', 'Your Manager')
        
        email_body = f"""To: {manager_name}
From: {employee_name}
Subject: {arguments['subject']}

{arguments['message']}

Best regards,
{employee_name}"""
        
        return json.dumps({
            'success': True,
            'action': 'email_manager',
            'employee_name': employee_name,
            'manager_name': manager_name,
            'subject': arguments['subject'],
            'email_draft': email_body
        })
    
    elif function_name == "schedule_hr_meeting":
        employee = find_employee(employees_df, arguments['employee_id'])
        name = 'Unknown Employee'
        emp_id_display = arguments['employee_id']
        if employee is not None:
            name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
            emp_id_display = employee.get('Employee ID', arguments['employee_id'])
        
        email_body = f"""Dear HR Team,

MEETING REQUEST
Employee: {name} (ID: {emp_id_display})

REASON FOR MEETING:
{arguments['reason']}

Please send a calendar invitation to schedule a meeting time with this employee.

Best regards,
HR Assistant Bot"""
        
        return json.dumps({
            'success': True,
            'action': 'schedule_hr_meeting',
            'employee_id': arguments['employee_id'],
            'name': name,
            'reason': arguments['reason'],
            'email_draft': email_body
        })
    
    return json.dumps({'success': False, 'error': 'Unknown function'})


# ================================================================
# AGENT SYSTEM
# ================================================================

class HRAgentSystem:
    def __init__(self, employees_df: pd.DataFrame, health_plans_df: pd.DataFrame):
        self.employees_df = employees_df
        self.health_plans_df = health_plans_df
        self.employee_conversations = {}
    
    async def chat(self, employee_id: str, message: str) -> dict:
        """Chat with the HR agent"""
        
        if employee_id not in self.employee_conversations:
            self.employee_conversations[employee_id] = []
        
        conversation = self.employee_conversations[employee_id]
        conversation.append({'role': 'user', 'content': message})
        
        # Keep last 20 messages
        if len(conversation) > 20:
            conversation = conversation[-20:]
            self.employee_conversations[employee_id] = conversation
        
        try:
            print(f"\n{'='*60}")
            print(f"EMPLOYEE: {employee_id}, MESSAGE: {message}")
            print(f"{'='*60}\n")
            
            # Call OpenAI with function calling
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT}
                ] + conversation,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            # If no tool calls, return the response
            if not tool_calls:
                assistant_message = response_message.content
                conversation.append({'role': 'assistant', 'content': assistant_message})
                print(f"\n📤 RESPONSE: {assistant_message}\n")
                return {'success': True, 'response': assistant_message}
            
            # Handle tool calls
            conversation.append(response_message.model_dump())
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                function_response = execute_function(
                    function_name,
                    function_args,
                    self.employees_df,
                    self.health_plans_df
                )
                
                conversation.append({
                    'role': 'tool',
                    'tool_call_id': tool_call.id,
                    'name': function_name,
                    'content': function_response
                })
            
            # Get final response after tool calls
            final_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT}
                ] + conversation,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            assistant_message = final_response.choices[0].message.content
            conversation.append({'role': 'assistant', 'content': assistant_message})
            
            print(f"\n📤 FINAL RESPONSE: {assistant_message}\n")
            
            return {
                'success': True,
                'response': assistant_message
            }
            
        except Exception as e:
            import traceback
            print(f"\n❌ ERROR:")
            print(traceback.format_exc())
            
            return {
                'success': False,
                'response': f"I apologize, but I encountered an issue: {str(e)}",
                'error': str(e)
            }
