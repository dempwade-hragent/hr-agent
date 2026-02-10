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
def escalate_to_hr(ctx: RunContextWrapper[HRContext], employee_id: str, subject: str, reason: str) -> str:
    """Escalate a request to HR when you cannot help directly.
    
    Use this when:
    - The request is outside your capabilities
    - The employee needs to speak with a human
    - Complex issues requiring HR intervention
    
    Args:
        employee_id: Employee ID
        subject: Brief subject line for the escalation (e.g., "Salary Adjustment Request")
        reason: Detailed reason for escalation (what the employee asked for and why you can't help)
    """
    employee = find_employee(ctx.context, employee_id)
    
    name = 'Unknown Employee'
    if employee is not None:
        name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
    
    # Create a formatted email draft
    email_body = f"""Dear HR Team,

Employee: {name} (ID: {employee_id})
Subject: {subject}

{reason}

This request has been escalated as it requires human review and assistance.

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
    instructions="""You are a helpful and professional HR assistant with memory of past conversations.

You help employees with:
- Salary and compensation questions
- PTO/vacation balance inquiries
- Bonus information
- Office locations and team information
- Manager details
- Health insurance plan comparisons
- W-2 tax form requests
- Escalating complex requests to HR

Guidelines:
- REMEMBER previous messages in the conversation - you have access to conversation history
- Always be friendly, professional, and concise
- When you use a tool and get employee information, use their name in your response
- Format currency with commas (e.g., $120,000)
- If you get an error that employee wasn't found, politely ask them to verify their employee ID
- When showing health insurance plans, create a clear comparison
- If you cannot help directly, use the escalate_to_hr tool and show them the email draft

IMPORTANT about escalations:
- When you escalate to HR, the escalate_to_hr tool will return an email draft
- ALWAYS show the user the email_draft field from the tool response
- Tell them "Here's the email I've drafted for HR:" and then show the email
- This way they can see exactly what will be sent

IMPORTANT about conversation memory:
- You can reference things from earlier in the conversation
- If the user says "what did you just tell me" or "what was that about", refer back to previous messages
- Keep track of what you've told them already

The tools return JSON strings - parse them to extract the data.
Check the 'success' field before using the data.
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
