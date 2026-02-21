"""
HR Agent - WORKING VERSION WITH SIMPLE INSTRUCTIONS
===================================================
Using original working imports, just simpler instructions
"""

from openai import OpenAI
from openai.agents import Agent, function_tool, RunContextWrapper
import pandas as pd
import json
from typing import Optional

# Context class
class HRContext:
    def __init__(self, employees_df: pd.DataFrame, health_plans_df: pd.DataFrame):
        self.employees_df = employees_df
        self.health_plans_df = health_plans_df


def find_employee(context: HRContext, employee_id: str) -> Optional[dict]:
    """Find employee by ID or first name"""
    df = context.employees_df
    
    # Try by Employee ID
    if employee_id.upper().startswith('EID'):
        match = df[df['Employee ID'].astype(str).str.strip().str.upper() == employee_id.upper()]
        if not match.empty:
            return match.iloc[0].to_dict()
    
    # Try by first name
    match = df[df['First Name'].astype(str).str.strip().str.lower() == employee_id.lower()]
    if not match.empty:
        return match.iloc[0].to_dict()
    
    return None


# ================================================================
# TOOLS
# ================================================================

@function_tool
def get_employee_salary(ctx: RunContextWrapper[HRContext], employee_id: str) -> str:
    """Get employee salary"""
    print(f"🔧 TOOL CALLED: get_employee_salary({employee_id})")
    employee = find_employee(ctx.context, employee_id)
    
    if employee is None:
        return json.dumps({'success': False, 'error': 'Employee not found'})
    
    return json.dumps({
        'success': True,
        'salary': employee.get('Salary', 'Unknown')
    })


@function_tool
def get_pto_balance(ctx: RunContextWrapper[HRContext], employee_id: str) -> str:
    """Get PTO balance"""
    print(f"🔧 TOOL CALLED: get_pto_balance({employee_id})")
    employee = find_employee(ctx.context, employee_id)
    
    if employee is None:
        return json.dumps({'success': False, 'error': 'Employee not found'})
    
    pto_column = 'Days Off Remaining' if 'Days Off Remaining' in ctx.context.employees_df.columns else 'Days Off'
    
    return json.dumps({
        'success': True,
        'pto_remaining': employee.get(pto_column, 'Unknown')
    })


@function_tool
def get_health_insurance_plans(ctx: RunContextWrapper[HRContext]) -> str:
    """Get available health insurance plans"""
    print(f"🔧 TOOL CALLED: get_health_insurance_plans()")
    
    plans = []
    for _, plan in ctx.context.health_plans_df.iterrows():
        plans.append({
            'name': plan['Plan Name'],
            'type': plan['Plan Type'],
            'employee_cost': plan['Employee Monthly Cost'],
            'family_cost': plan['Family Monthly Cost'],
            'deductible': plan['Deductible']
        })
    
    return json.dumps({'success': True, 'plans': plans})


@function_tool
def escalate_to_hr(ctx: RunContextWrapper[HRContext], employee_id: str, subject: str, reason: str) -> str:
    """Escalate request to HR - use when employee wants to enroll, change benefits, get a raise, etc."""
    print(f"🚨 TOOL CALLED: escalate_to_hr({employee_id}, {subject})")
    
    employee = find_employee(ctx.context, employee_id)
    
    name = 'Unknown Employee'
    emp_id_display = employee_id
    if employee is not None:
        name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
        emp_id_display = employee.get('Employee ID', employee_id)
    
    email_body = f"""Dear HR Team,

Employee: {name} (ID: {emp_id_display})
Subject: {subject}

REQUEST DETAILS:
{reason}

This request has been escalated for your review and assistance.

Best regards,
HR Assistant Bot"""
    
    return json.dumps({
        'success': True,
        'action': 'escalate_to_hr',
        'employee_id': employee_id,
        'name': name,
        'subject': subject,
        'reason': reason,
        'email_draft': email_body,
        'recipient': 'hr@company.com'
    })


@function_tool
def email_manager(ctx: RunContextWrapper[HRContext], employee_id: str, subject: str, message: str) -> str:
    """Draft email to employee's manager - use for PTO requests, questions, etc."""
    print(f"📧 TOOL CALLED: email_manager({employee_id}, {subject})")
    
    employee = find_employee(ctx.context, employee_id)
    
    if employee is None:
        return json.dumps({'success': False, 'error': 'Employee not found'})
    
    employee_name = employee.get('First Name', 'Unknown')
    manager_name = employee.get('Manager', 'Your Manager')
    
    email_body = f"""To: {manager_name}
From: {employee_name}
Subject: {subject}

{message}

Best regards,
{employee_name}"""
    
    return json.dumps({
        'success': True,
        'action': 'email_manager',
        'employee_name': employee_name,
        'manager_name': manager_name,
        'subject': subject,
        'email_draft': email_body
    })


@function_tool
def schedule_hr_meeting(ctx: RunContextWrapper[HRContext], employee_id: str, reason: str) -> str:
    """Schedule meeting with HR"""
    print(f"📅 TOOL CALLED: schedule_hr_meeting({employee_id})")
    
    employee = find_employee(ctx.context, employee_id)
    
    name = 'Unknown Employee'
    emp_id_display = employee_id
    if employee is not None:
        name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
        emp_id_display = employee.get('Employee ID', employee_id)
    
    email_body = f"""Dear HR Team,

MEETING REQUEST
Employee: {name} (ID: {emp_id_display})

REASON FOR MEETING:
{reason}

Please send a calendar invitation to schedule a meeting time with this employee.

Best regards,
HR Assistant Bot"""
    
    return json.dumps({
        'success': True,
        'action': 'schedule_hr_meeting',
        'employee_id': employee_id,
        'name': name,
        'reason': reason,
        'email_draft': email_body
    })


# ================================================================
# AGENT - ULTRA SIMPLE INSTRUCTIONS
# ================================================================

hr_agent = Agent(
    name="HR Assistant",
    model="gpt-4o",
    instructions="""You are a helpful HR assistant. Answer questions directly and use tools when needed.

SIMPLE RULES:

1. When user asks "what are my 401k options?":
   - Answer: "Company offers 401(k) with matching. Would you like to enroll?"
   - If they say YES/ENROLL: Call escalate_to_hr with subject="401(k) Enrollment Request"

2. When user asks "can I take [day] off?":
   - Call get_pto_balance first
   - Then say: "You have X days. I can email your manager. Would you like that?"
   - If they say YES: Call email_manager with the PTO request

3. When user says YES to something you offered:
   - DO that thing immediately
   - DON'T ask "what do you want?"

4. After calling escalate_to_hr or email_manager:
   - Parse the JSON response
   - Extract the "email_draft" field
   - Show it to the user
   - Ask "Would you like me to send this?"

5. When user says "send it":
   - Say "Email sent. HR/Manager will follow up."

BE DIRECT. CALL TOOLS. SHOW DRAFTS.""",
    tools=[
        get_employee_salary,
        get_pto_balance,
        get_health_insurance_plans,
        escalate_to_hr,
        email_manager,
        schedule_hr_meeting
    ]
)


# ================================================================
# AGENT SYSTEM
# ================================================================

class HRAgentSystem:
    def __init__(self, employees_df: pd.DataFrame, health_plans_df: pd.DataFrame):
        self.context = HRContext(employees_df, health_plans_df)
        self.client = OpenAI()
        self.employee_conversations = {}
    
    async def chat(self, employee_id: str, message: str) -> dict:
        """Chat with the HR agent"""
        
        if employee_id not in self.employee_conversations:
            self.employee_conversations[employee_id] = []
        
        conversation = self.employee_conversations[employee_id]
        conversation.append({'role': 'user', 'content': message})
        
        if len(conversation) > 20:
            conversation = conversation[-20:]
            self.employee_conversations[employee_id] = conversation
        
        try:
            print(f"\n{'='*60}")
            print(f"EMPLOYEE: {employee_id}, MESSAGE: {message}")
            print(f"{'='*60}\n")
            
            result = hr_agent.run(
                context=self.context,
                messages=conversation
            )
            
            response_text = ""
            for msg in result.messages:
                if hasattr(msg, 'content') and msg.content:
                    for content in msg.content:
                        if hasattr(content, 'text'):
                            response_text += content.text + "\n"
            
            response_text = response_text.strip()
            print(f"\n📤 RESPONSE: {response_text[:200]}...\n")
            
            conversation.append({'role': 'assistant', 'content': response_text})
            
            return {
                'success': True,
                'response': response_text
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
