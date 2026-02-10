"""
HR Agent SDK - OpenAI Agents SDK Version (2025)
================================================

Uses the modern Agents SDK with:
- Agent and Runner pattern
- @function_tool decorators
- RunContextWrapper for state management
- Clean, maintainable code

NO MORE:
- Manual Assistants API calls
- Thread management
- Complex error handling

IT JUST WORKS! 🎉
"""

from agents import Agent, Runner, function_tool, RunContextWrapper
from dataclasses import dataclass, field
from typing import Optional
import pandas as pd
import json


# ================================================================
# SHARED CONTEXT (State)
# ================================================================

@dataclass
class HRContext:
    """
    Shared state for HR operations.
    Contains employee data and health plan information.
    """
    employees_df: pd.DataFrame
    health_plans_df: Optional[pd.DataFrame] = None
    conversation_history: list[dict] = field(default_factory=list)


# ================================================================
# HELPER FUNCTION - Find Employee
# ================================================================

def find_employee(ctx: HRContext, employee_id: str) -> Optional[pd.Series]:
    """
    Smart employee finder that handles multiple formats:
    - EID format: "EID2480001"
    - Numeric: "1", "2", "3"
    - First name: "Thomas", "KobeBean"
    - Full name: "Thomas Anderson"
    """
    employee_id = str(employee_id).strip()
    df = ctx.employees_df
    
    # Case 1: EID format
    if employee_id.startswith('EID'):
        match = df[df['Employee ID'].astype(str).str.strip() == employee_id]
        if not match.empty:
            return match.iloc[0]
    
    # Case 2: Numeric ID
    if employee_id.isdigit():
        match = df[df['Employee ID'].astype(str).str.strip() == employee_id]
        if not match.empty:
            return match.iloc[0]
    
    # Case 3: First Name
    if 'First Name' in df.columns:
        match = df[df['First Name'].astype(str).str.strip().str.lower() == employee_id.lower()]
        if not match.empty:
            return match.iloc[0]
    
    # Case 4: Employee Name (if exists)
    if 'Employee Name' in df.columns:
        match = df[df['Employee Name'].astype(str).str.strip().str.lower() == employee_id.lower()]
        if not match.empty:
            return match.iloc[0]
        
        # Partial match
        match = df[df['Employee Name'].astype(str).str.strip().str.lower().str.contains(employee_id.lower(), na=False)]
        if not match.empty:
            return match.iloc[0]
    
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
        employee_id: Employee ID (e.g., 'EID2480001', '1', or first name like 'Thomas')
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
        employee_id: Employee ID (e.g., 'EID2480001', '1', or first name like 'Thomas')
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
        employee_id: Employee ID (e.g., 'EID2480001', '1', or first name like 'Thomas')
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
        employee_id: Employee ID (e.g., 'EID2480001', '1', or first name like 'Thomas')
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
        employee_id: Employee ID (e.g., 'EID2480001', '1', or first name like 'Thomas')
    """
    employee = find_employee(ctx.context, employee_id)
    
    if employee is None:
        return json.dumps({
            'success': False,
            'error': f'Employee not found: {employee_id}'
        })
    
    name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
    
    # Try different column names for manager
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
        employee_id: Employee ID (e.g., 'EID2480001', '1', or first name like 'Thomas')
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
def escalate_to_hr(ctx: RunContextWrapper[HRContext], employee_id: str, subject: str, message: str) -> str:
    """Draft an email to HR for requests requiring human assistance.
    
    Args:
        employee_id: Employee ID (e.g., 'EID2480001', '1', or first name like 'Thomas')
        subject: Email subject line
        message: Detailed message describing the request
    """
    employee = find_employee(ctx.context, employee_id)
    
    name = 'Unknown'
    if employee is not None:
        name = employee.get('First Name', employee.get('Employee Name', 'Unknown'))
    
    return json.dumps({
        'success': True,
        'action': 'email_hr',
        'employee_id': employee_id,
        'name': name,
        'subject': subject,
        'message': message,
        'recipient': 'hr@company.com'
    })


# ================================================================
# MAIN HR AGENT
# ================================================================

hr_agent = Agent(
    name="HR Assistant",
    instructions="""You are a helpful and professional HR assistant.

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
- Always be friendly, professional, and concise
- When you use a tool and get employee information, use their name in your response
- Format currency with commas (e.g., $120,000 not 120000)
- If you get an error that employee wasn't found, politely ask them to verify their employee ID
- When showing health insurance plans, create a clear comparison
- If you cannot help directly, offer to escalate to HR
- Keep responses natural and conversational, not robotic

Important:
- The tools return JSON strings - parse them to extract the data
- Check the 'success' field in tool responses before using the data
- If success is False, tell the user there was an error and offer alternatives
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
    model="gpt-4o-mini",  # Cost-effective and fast
)


# ================================================================
# MAIN INTERFACE
# ================================================================

class HRAgentSystem:
    """
    Main interface for the HR Agent system.
    Handles initialization and chat interactions.
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
        
        print(f"✅ HR Agent System initialized")
        print(f"   Employees loaded: {len(employees_df)}")
        print(f"   Employee ID format: {employees_df['Employee ID'].dtype}")
        print(f"   Sample IDs: {list(employees_df['Employee ID'].astype(str).head(3))}")
    
    async def chat(self, employee_id: str, message: str) -> dict:
        """
        Send a message to the HR agent.
        
        Args:
            employee_id: The employee asking the question
            message: The employee's question
        
        Returns:
            Dict with 'success' and 'response' fields
        """
        try:
            # Construct the full message with employee context
            full_message = f"[Employee ID: {employee_id}] {message}"
            
            # Run the agent
            result = await Runner.run(
                hr_agent,
                input=full_message,
                context=self.context
            )
            
            return {
                'success': True,
                'response': result.final_output,
                'method': 'openai_agents_sdk_2025'
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


# ================================================================
# EXAMPLE USAGE
# ================================================================

async def demo():
    """Demo the HR Agent system"""
    
    # Create sample employee data
    sample_employees = pd.DataFrame({
        'Employee ID': ['EID2480001', 'EID2480002', 'EID2480003'],
        'First Name': ['Thomas', 'Sarah', 'KobeBean'],
        'Salary': [120000, 95000, 150000],
        'Bonus %': [10, 8, 15],
        'Days Off Remaining': [15, 8, 20],
        'Team': ['Engineering', 'Sales', 'Product'],
        'Location': ['New York', 'San Francisco', 'Austin'],
        'On-site': ['Hybrid', 'Remote', 'On-site']
    })
    
    sample_health_plans = pd.DataFrame({
        'Plan Name': ['Blue Shield PPO Gold', 'Kaiser HMO Silver'],
        'Plan Type': ['PPO', 'HMO'],
        'Employee Cost (Monthly)': [250, 150],
        'Family Cost (Monthly)': [650, 400],
        'Deductible': [500, 1000]
    })
    
    # Initialize system
    hr_system = HRAgentSystem(
        employees_df=sample_employees,
        health_plans_df=sample_health_plans
    )
    
    # Test questions
    questions = [
        ("EID2480001", "What's my salary?"),
        ("Thomas", "How many PTO days do I have?"),
        ("EID2480003", "What's my bonus?"),
        ("Sarah", "What are the health insurance options?"),
    ]
    
    for emp_id, question in questions:
        print(f"\n{'='*60}")
        print(f"Employee: {emp_id}")
        print(f"Question: {question}")
        print(f"{'='*60}")
        
        response = await hr_system.chat(emp_id, question)
        print(f"\nResponse: {response['response']}\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())
