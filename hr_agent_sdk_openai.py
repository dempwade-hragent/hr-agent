"""
HR Agent SDK - OpenAI Agents SDK Version with Memory
=====================================================

Enhanced with:
- Conversation history tracking (memory across messages)
- Better escalation handling
- Clearer responses for HR escalations

Uses the Agents SDK from: openai-agents package
"""

from agents import Agent, Runner, RunContextWrapper, function_tool
from dataclasses import dataclass, field
from typing import Optional
import pandas as pd
import json


# ================================================================
# SHARED CONTEXT (State with Conversation History)
# ================================================================

@dataclass
class HRContext:
    """
    Shared state for HR operations.
    Contains employee data, health plan info, and conversation history.
    """
    employees_df: pd.DataFrame
    health_plans_df: Optional[pd.DataFrame] = None
    conversation_history: list[dict] = field(default_factory=list)
    current_employee_id: Optional[str] = None


# ================================================================
# HELPER FUNCTION - Find Employee
# ================================================================

def find_employee(ctx: HRContext, employee_id: str) -> Optional[pd.Series]:
    """
    Smart employee finder that handles multiple formats.
    """
    employee_id = str(employee_id).strip()
    df = ctx.employees_df
    
    # Case 1: EID format
    if employee_id.startswith('EID'):
        match = df[df['Employee ID'].astype(str).str.strip() == employee_id]
        if not match.empty:
            print(f"✅ Found employee by EID: {employee_id}")
            return match.iloc[0]
    
    # Case 2: Numeric ID
    if employee_id.isdigit():
        match = df[df['Employee ID'].astype(str).str.strip() == employee_id]
        if not match.empty:
            print(f"✅ Found employee by numeric ID: {employee_id}")
            return match.iloc[0]
    
    # Case 3: First Name
    if 'First Name' in df.columns:
        match = df[df['First Name'].astype(str).str.strip().str.lower() == employee_id.lower()]
        if not match.empty:
            print(f"✅ Found employee by First Name: {employee_id}")
            return match.iloc[0]
    
    print(f"❌ Could not find employee: {employee_id}")
    return None


# ================================================================
# FUNCTION TOOLS - Employee Information
# ================================================================

@function_tool
def get_employee_salary(ctx: RunContextWrapper[HRContext], employee_id: str) -> str:
    """Get the salary for an employee.
    
    Args:
        employee_id: Employee ID (e.g., 'EID2480001', '1', or first name like 'Thomas')
    """
    employee = find_employee(ctx.context, employee_id)
    
    if employee is None:
        return json.dumps({
            'success': False,
            'error': f'Employee not found: {employee_id}'
        })
    
    name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
    salary = employee.get('Salary', 0)
    
    return json.dumps({
        'success': True,
        'name': name,
        'salary': int(salary),
        'formatted_salary': f'${int(salary):,}'
    })


@function_tool
def get_pto_balance(ctx: RunContextWrapper[HRContext], employee_id: str) -> str:
    """Get remaining PTO (paid time off) days for an employee.
    
    Args:
        employee_id: Employee ID
    """
    employee = find_employee(ctx.context, employee_id)
    
    if employee is None:
        return json.dumps({
            'success': False,
            'error': f'Employee not found: {employee_id}'
        })
    
    name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
    days_off = employee.get('Days Off Remaining', employee.get('Days Off', 0))
    
    return json.dumps({
        'success': True,
        'name': name,
        'days_remaining': int(days_off)
    })


@function_tool
def get_bonus_info(ctx: RunContextWrapper[HRContext], employee_id: str) -> str:
    """Get bonus percentage for an employee.
    
    Args:
        employee_id: Employee ID
    """
    employee = find_employee(ctx.context, employee_id)
    
    if employee is None:
        return json.dumps({
            'success': False,
            'error': f'Employee not found: {employee_id}'
        })
    
    name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
    bonus_pct = employee.get('Bonus %', 0)
    salary = employee.get('Salary', 0)
    bonus_amount = int(salary) * int(bonus_pct) / 100
    
    return json.dumps({
        'success': True,
        'name': name,
        'bonus_percentage': int(bonus_pct),
        'bonus_amount': int(bonus_amount),
        'formatted_bonus': f'${int(bonus_amount):,}'
    })


@function_tool
def get_location(ctx: RunContextWrapper[HRContext], employee_id: str) -> str:
    """Get the office location where an employee works.
    
    Args:
        employee_id: Employee ID
    """
    employee = find_employee(ctx.context, employee_id)
    
    if employee is None:
        return json.dumps({
            'success': False,
            'error': f'Employee not found: {employee_id}'
        })
    
    name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
    location = employee.get('Location', 'Unknown')
    on_site = employee.get('On-site', 'Unknown')
    
    return json.dumps({
        'success': True,
        'name': name,
        'location': location,
        'on_site': on_site
    })


@function_tool
def get_team_info(ctx: RunContextWrapper[HRContext], employee_id: str) -> str:
    """Get the team/department an employee belongs to.
    
    Args:
        employee_id: Employee ID
    """
    employee = find_employee(ctx.context, employee_id)
    
    if employee is None:
        return json.dumps({
            'success': False,
            'error': f'Employee not found: {employee_id}'
        })
    
    name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
    team = employee.get('Team', 'Unknown')
    
    return json.dumps({
        'success': True,
        'name': name,
        'team': team
    })


@function_tool
def get_manager_info(ctx: RunContextWrapper[HRContext], employee_id: str) -> str:
    """Get information about an employee's manager.
    
    Args:
        employee_id: Employee ID
    """
    employee = find_employee(ctx.context, employee_id)
    
    if employee is None:
        return json.dumps({
            'success': False,
            'error': f'Employee not found: {employee_id}'
        })
    
    name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
    manager = employee.get('Manager', employee.get('Manager Name', 'Unknown'))
    
    return json.dumps({
        'success': True,
        'name': name,
        'manager': manager
    })


@function_tool
def get_health_insurance_plans(ctx: RunContextWrapper[HRContext]) -> str:
    """Get all available health insurance plans with costs and coverage.
    
    No arguments needed - returns all plans.
    """
    if ctx.context.health_plans_df is None:
        return json.dumps({
            'success': False,
            'error': 'Health plans data not available'
        })
    
    plans = []
    for _, plan in ctx.context.health_plans_df.iterrows():
        plans.append({
            'name': plan['Plan Name'],
            'type': plan['Plan Type'],
            'employee_monthly': float(plan['Employee Cost (Monthly)']),
            'family_monthly': float(plan['Family Cost (Monthly)']),
            'deductible': float(plan['Deductible'])
        })
    
    return json.dumps({
        'success': True,
        'plans': plans
    })


@function_tool
def request_w2_form(ctx: RunContextWrapper[HRContext], employee_id: str) -> str:
    """Request W-2 tax form generation for an employee.
    
    Args:
        employee_id: Employee ID
    """
    employee = find_employee(ctx.context, employee_id)
    
    if employee is None:
        return json.dumps({
            'success': False,
            'error': f'Employee not found: {employee_id}'
        })
    
    name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
    emp_id = employee.get('Employee ID', 'Unknown')
    
    return json.dumps({
        'success': True,
        'action': 'w2_generation',
        'name': name,
        'employee_id': str(emp_id),
        'message': 'W-2 tax form generation initiated. You will receive a download link shortly.'
    })


@function_tool
def email_manager(ctx: RunContextWrapper[HRContext], employee_id: str, subject: str, message: str) -> str:
    """Draft an email to the employee's manager. Use when employee asks to email their manager.
    
    Common uses:
    - PTO requests
    - Status updates
    - Questions for manager
    - Any communication with direct manager
    
    Args:
        employee_id: Employee ID
        subject: Email subject line (e.g., "PTO Request for Tomorrow", "Question About Project X")
        message: The email body - include all relevant context from the conversation
    """
    employee = find_employee(ctx.context, employee_id)
    
    employee_name = 'Unknown Employee'
    manager_name = 'Your Manager'
    emp_id_display = employee_id
    
    if employee is not None:
        employee_name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
        emp_id_display = employee.get('Employee ID', employee_id)
        manager_name = employee.get('Manager', employee.get('Manager Name', 'Your Manager'))
    
    # Create a formatted email draft
    email_body = f"""To: {manager_name}
From: {employee_name}
Subject: {subject}

{message}

Best regards,
{employee_name}"""
    
    return json.dumps({
        'success': True,
        'action': 'email_manager',
        'employee_id': employee_id,
        'employee_name': employee_name,
        'manager_name': manager_name,
        'subject': subject,
        'message': message,
        'email_draft': email_body
    })


@function_tool
def schedule_hr_meeting(ctx: RunContextWrapper[HRContext], employee_id: str, reason: str) -> str:
    """Schedule a meeting with HR. Use when employee asks to meet with HR or schedule a calendar meeting.
    
    Args:
        employee_id: Employee ID
        reason: Why they want to meet (include any topics they mentioned from the conversation)
    """
    employee = find_employee(ctx.context, employee_id)
    
    name = 'Unknown Employee'
    emp_id_display = employee_id
    if employee is not None:
        name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
        emp_id_display = employee.get('Employee ID', employee_id)
    
    # Create a formatted meeting request email
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
        'action': 'schedule_meeting',
        'employee_id': employee_id,
        'name': name,
        'reason': reason,
        'email_draft': email_body,
        'recipient': 'hr@company.com'
    })


@function_tool
def escalate_to_hr(ctx: RunContextWrapper[HRContext], employee_id: str, subject: str, reason: str) -> str:
    """Escalate a request to HR. Use when the user asks for something you cannot do.
    
    IMPORTANT: Include FULL CONTEXT in the 'reason' parameter.
    - What did the user say they want?
    - What specific details did they provide?
    - What was the conversation about?
    
    Examples:
    - Subject: "Salary Increase Request", Reason: "Employee is requesting a salary increase to $500,000 per year. They stated they deserve this because they are the best performer."
    - Subject: "Meeting Request", Reason: "Employee wants to schedule a meeting with HR to discuss benefits."
    - Subject: "Policy Question", Reason: "Employee is asking about remote work policy and whether they can work from home 3 days per week."
    
    Args:
        employee_id: Employee ID
        subject: Brief subject line (e.g., "Salary Increase Request", "Meeting Request")
        reason: DETAILED explanation including what the user said they want and any context from the conversation
    """
    employee = find_employee(ctx.context, employee_id)
    
    name = 'Unknown Employee'
    emp_id_display = employee_id
    if employee is not None:
        name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
        emp_id_display = employee.get('Employee ID', employee_id)
    
    # Create a formatted email draft with ALL the context
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


# ================================================================
# MAIN HR AGENT
# ================================================================

hr_agent = Agent(
    name="HR Assistant",
    instructions="""You are a direct, solution-oriented HR assistant. GET THINGS DONE.

CORE BEHAVIOR:
- Answer questions directly and concisely
- Don't ask for more information unless absolutely essential
- Don't make small talk or be overly conversational
- Execute requests immediately - don't explain what you're going to do, just do it
- Remember previous messages in the conversation
- When users make casual statements ("Nice!", "Thanks!", "Cool!"), acknowledge briefly or don't respond with data

WHAT YOU CAN DO:
- Answer: salary, PTO balance, bonus, location, team, manager
- Show health insurance plans: Use get_health_insurance_plans to show all available plans with costs
- Generate: W-2 forms
- Email manager: Draft emails to employee's manager (PTO requests, questions, updates)
- Schedule: meetings with HR (use schedule_hr_meeting tool)

WHAT YOU CANNOT DO (ESCALATE THESE):
- Approve raises or salary changes
- Enroll in or change health insurance plans
- Approve PTO/vacation requests (only managers can approve)
- Make policy decisions

EMAILING YOUR MANAGER:
When user asks to "email my manager" or "help me email my manager":
- Use email_manager tool
- For PTO requests: Include how many days, when, and any context from conversation
- Show them the email draft

Example PTO request email:
User: "Can I take a day off tomorrow?"
You: "You have 13 PTO days remaining. To request time off, ask your manager for approval."
User: "Can you help me email my manager?"
You: [call email_manager with subject: "PTO Request for Tomorrow", message: "I would like to request a day off tomorrow, [date]. I currently have 13 PTO days remaining. Please let me know if this works. Thank you!"]
You: "Here's the email draft:

To: [Manager Name]
From: [Employee Name]
Subject: PTO Request for Tomorrow

I would like to request a day off tomorrow, [date]. I currently have 13 PTO days remaining. Please let me know if this works. Thank you!
..."

HEALTH INSURANCE:
When user asks "what are my health insurance options" or "show me health plans":
✅ CORRECT: Use get_health_insurance_plans tool, show all plans with costs
❌ WRONG: Escalate to HR

When user asks to "enroll" or "change plans" or "sign up":
✅ CORRECT: Escalate to HR (you cannot change enrollment)

RESPONSE STYLE:
✅ GOOD: "Your salary is $61,933."
❌ BAD: "I'd be happy to help you with that! Let me check your salary information for you..."

✅ GOOD: "You have 15 PTO days remaining."
❌ BAD: "Of course! I can help you with your PTO balance. Let me look that up..."

PTO REQUEST HANDLING:
User: "Can I take a day off next week?"
✅ CORRECT: "You have 13 PTO days remaining. To request time off, submit it through your company's PTO system or ask your manager for approval."
❌ WRONG: "You can take a day off next week." (You cannot approve PTO!)

CASUAL CONVERSATION:
User: "Nice!" or "Thanks!" or "Cool!"
✅ CORRECT: "You're welcome." or "Let me know if you need anything else."
❌ WRONG: "Your salary is $61,933." (Don't repeat random data!)

MEETING REQUESTS:
When user asks to "schedule a meeting" or "meet with HR":
- Use schedule_hr_meeting tool immediately
- Include any context they mentioned (what they want to discuss)
- Show them the email draft

ESCALATIONS (raise requests, policy changes, complex issues):
When user asks for something you can't do (raise, policy change):
1. Call escalate_to_hr with EXACT details from the conversation
2. In 'reason', quote what they said: "Employee wants X because Y"
3. Show the email draft

Example conversations:

User: "Can I take a day off tomorrow?"
You: "You have 13 PTO days remaining. To request time off, ask your manager for approval."
User: "Can you help me email my manager?"
You: [call email_manager with subject: "PTO Request for Tomorrow", message: "I would like to request a day off tomorrow, February 20th, 2026. I currently have 13 PTO days remaining. Please let me know if this works. Thank you!"]
You: "Here's the email draft:

To: [Manager Name]
From: [Employee Name]
Subject: PTO Request for Tomorrow

I would like to request a day off tomorrow, February 20th, 2026. I currently have 13 PTO days remaining. Please let me know if this works. Thank you!

Best regards,
[Employee Name]"

User: "What are my health insurance options?"
You: [call get_health_insurance_plans]
You: "Here are the available health insurance plans:

1. Blue Shield PPO Gold - $250/month (employee), $650/month (family), $500 deductible
2. Kaiser HMO Silver - $150/month (employee), $400/month (family), $1000 deductible
..."

User: "I want to enroll in the PPO plan"
You: [call escalate_to_hr with subject: "Health Insurance Enrollment Request", reason: "Employee wants to enroll in the Blue Shield PPO Gold plan."]
You: "I've escalated your enrollment request. Here's the email: [show email_draft]"

User: "I want a raise to $500k"
You: [call escalate_to_hr with reason: "Employee is requesting a salary increase to $500,000 per year."]
You: "I've escalated your raise request to HR. Here's the email:
[show email_draft]"

User: "Can I schedule a meeting with HR?"
You: [call schedule_hr_meeting with reason: "Employee wants to schedule a meeting with HR."]
You: "Meeting request sent to HR. Here's the email:
[show email_draft]"

CRITICAL RULES:
- NEVER approve PTO, raises, or any requests requiring manager/HR approval
- NEVER escalate simple questions you have tools for (salary, PTO, health plan OPTIONS)
- ONLY escalate when user wants to CHANGE something (enroll, raise, etc.)
- When user asks to "email my manager", use email_manager tool (not escalate_to_hr or schedule_hr_meeting)
- For manager emails: Include context from recent conversation (like PTO details)
- NEVER ask the user to verify their employee ID - you already have it from the system
- NEVER ask for "more details" on escalations - just escalate with what they said
- NEVER say "I can help with that" - just help
- Tools return JSON - parse it and extract data
- For escalations/meetings/manager emails: Parse the JSON, extract 'email_draft' field, and SHOW IT to the user
- When showing email drafts, say "Here's the email draft:" then show the FULL email_draft content

Be efficient. Be direct. Get it done.
""",
    tools=[
        get_employee_salary,
        get_pto_balance,
        get_bonus_info,
        get_location,
        get_team_info,
        get_manager_info,
        get_health_insurance_plans,
        request_w2_form,
        email_manager,
        schedule_hr_meeting,
        escalate_to_hr,
    ],
    model="gpt-4o-mini",
)


# ================================================================
# MAIN INTERFACE
# ================================================================

class HRAgentSystem:
    """
    Main interface for the HR Agent system with conversation memory.
    """
    
    def __init__(self, employees_df: pd.DataFrame, health_plans_df: Optional[pd.DataFrame] = None):
        """
        Initialize the HR Agent system.
        
        Args:
            employees_df: DataFrame containing employee data
            health_plans_df: Optional DataFrame containing health insurance plans
        """
        self.context = HRContext(
            employees_df=employees_df,
            health_plans_df=health_plans_df
        )
        
        # Store separate conversation histories per employee
        self.employee_conversations = {}
        
        print(f"✅ HR Agent System initialized")
        print(f"   Employees loaded: {len(employees_df)}")
        print(f"   Employee ID format: {employees_df['Employee ID'].dtype}")
        print(f"   Sample IDs: {list(employees_df['Employee ID'].astype(str).head(3))}")
    
    async def chat(self, employee_id: str, message: str) -> dict:
        """
        Send a message to the HR agent with conversation memory.
        
        Args:
            employee_id: The employee asking the question
            message: The employee's question
        
        Returns:
            Dict with 'success' and 'response' fields
        """
        try:
            # Get or create conversation history for this employee
            if employee_id not in self.employee_conversations:
                self.employee_conversations[employee_id] = []
            
            conversation = self.employee_conversations[employee_id]
            
            # Construct the message with employee context
            full_message = f"[Employee ID: {employee_id}] {message}"
            
            # Run the agent with full conversation history
            result = await Runner.run(
                hr_agent,
                input=full_message,
                context=self.context
            )
            
            # Store the conversation
            conversation.append({
                'role': 'user',
                'content': message
            })
            conversation.append({
                'role': 'assistant',
                'content': result.final_output
            })
            
            # Keep only last 20 messages to avoid huge context
            if len(conversation) > 20:
                conversation = conversation[-20:]
                self.employee_conversations[employee_id] = conversation
            
            return {
                'success': True,
                'response': result.final_output,
                'method': 'openai_agents_sdk_with_memory'
            }
        
        except Exception as e:
            print(f"❌ Error in chat: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'response': "I apologize, but I encountered an error processing your request. Please try again.",
                'error': str(e)
            }
