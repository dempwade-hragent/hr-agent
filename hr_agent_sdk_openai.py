"""
HR Agent - WORKING VERSION WITH SIMPLE INSTRUCTIONS
===================================================
Using correct imports for openai-agents package
"""

from openai import OpenAI
from agents import Agent, function_tool, RunContextWrapper
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

BE DIRECT. CALL TOOLS. REMEMBER CONTEXT.""",
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
