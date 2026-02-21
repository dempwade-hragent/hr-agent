"""
HR Agent - FIXED VERSION
========================
Ultra-simple trigger-based instructions that actually work
"""

from openai import OpenAI
from agents import Agent, function_tool
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
def get_employee_salary(ctx, employee_id: str) -> str:
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
def get_pto_balance(ctx, employee_id: str) -> str:
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
def get_health_insurance_plans(ctx) -> str:
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
def escalate_to_hr(ctx, employee_id: str, subject: str, reason: str) -> str:
    """Escalate request to HR"""
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
def email_manager(ctx, employee_id: str, subject: str, message: str) -> str:
    """Draft email to employee's manager"""
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
def schedule_hr_meeting(ctx, employee_id: str, reason: str) -> str:
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
# AGENT WITH ULTRA-SIMPLE INSTRUCTIONS
# ================================================================

hr_agent = Agent(
    name="HR Assistant",
    model="gpt-4o",
    instructions="""You are an HR assistant. Your job is to help employees with HR questions.

SUPER SIMPLE RULES - FOLLOW EXACTLY:

1. WHEN USER ASKS ABOUT 401(k):
   - First time: Say "Company offers 401(k) with matching. Would you like to enroll?"
   - If they say YES/ENROLL/SIGN ME UP: Call escalate_to_hr with subject "401(k) Enrollment Request"

2. WHEN USER ASKS ABOUT PTO FOR SPECIFIC DAY:
   - First show PTO balance
   - Then say: "I can email your manager to request approval. Would you like me to do that?"
   - If they say YES: Call email_manager with PTO request details

3. WHEN USER SAYS "YES" OR "SURE" OR "OKAY":
   - Look at what you JUST offered in your previous message
   - Do that thing immediately
   - DO NOT ask "what do you want?" - you JUST told them what you can do

4. KEYWORDS THAT TRIGGER TOOLS:
   - "enroll" + "401k" context = Call escalate_to_hr for 401k enrollment
   - "enroll" + "health" context = Call escalate_to_hr for health enrollment  
   - "email manager" = Call email_manager
   - "schedule meeting" = Call schedule_hr_meeting
   - User says "yes" after you offered something = Do that thing

5. AFTER CALLING A TOOL:
   - The tool returns JSON with "email_draft"
   - Extract the email_draft
   - Show it to the user
   - Ask "Would you like me to send this?"

6. WHEN USER SAYS "SEND IT" OR "YES SEND IT":
   - Say "Email sent to [recipient]. They'll follow up shortly."
   - DO NOT ask which email

EXAMPLES OF CORRECT BEHAVIOR:

Example 1 - 401k:
User: "What are my 401k options?"
You: "Company offers 401(k) with matching. Would you like to enroll?"
User: "yes"
You: [Call escalate_to_hr NOW]
You: "I've sent this to HR: [show email_draft]"

Example 2 - PTO:
User: "Can I take Monday off?"
You: [Call get_pto_balance]
You: "You have 13 days remaining. I can email your manager. Would you like me to do that?"
User: "yes"
You: [Call email_manager NOW]
You: "Here's the draft: [show email_draft]"

THINGS TO NEVER SAY:
- "What would you like to enroll in?" (if you were just talking about 401k)
- "What can I assist you with?" (if they just said yes to your offer)
- "Could you clarify?" (if they said yes to something you offered)

BE DIRECT. CALL TOOLS. SHOW EMAILS. GET IT DONE.
""",
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
# AGENT SYSTEM WITH CONVERSATION MEMORY
# ================================================================

class HRAgentSystem:
    def __init__(self, employees_df: pd.DataFrame, health_plans_df: pd.DataFrame):
        self.context = HRContext(employees_df, health_plans_df)
        self.client = OpenAI()
        self.employee_conversations = {}
    
    async def chat(self, employee_id: str, message: str) -> dict:
        """Chat with the HR agent"""
        
        # Initialize conversation history for this employee
        if employee_id not in self.employee_conversations:
            self.employee_conversations[employee_id] = []
        
        conversation = self.employee_conversations[employee_id]
        
        # Add user message
        conversation.append({
            'role': 'user',
            'content': message
        })
        
        # Keep only last 20 messages to avoid huge context
        if len(conversation) > 20:
            conversation = conversation[-20:]
            self.employee_conversations[employee_id] = conversation
        
        try:
            print(f"\n{'='*60}")
            print(f"EMPLOYEE: {employee_id}")
            print(f"MESSAGE: {message}")
            print(f"CONVERSATION HISTORY: {len(conversation)} messages")
            print(f"{'='*60}\n")
            
            # Run the agent
            result = hr_agent.run(
                context=self.context,
                messages=conversation
            )
            
            # Extract response
            response_text = ""
            for message in result.messages:
                if hasattr(message, 'content') and message.content:
                    for content in message.content:
                        if hasattr(content, 'text'):
                            response_text += content.text + "\n"
            
            response_text = response_text.strip()
            
            print(f"\n📤 RESPONSE: {response_text[:200]}...")
            
            # Add assistant response to conversation
            conversation.append({
                'role': 'assistant',
                'content': response_text
            })
            
            return {
                'success': True,
                'response': response_text
            }
            
        except Exception as e:
            import traceback
            print(f"\n❌ ERROR in chat:")
            print(traceback.format_exc())
            
            return {
                'success': False,
                'response': f"I apologize, but I encountered an error: {str(e)}",
                'error': str(e)
            }
