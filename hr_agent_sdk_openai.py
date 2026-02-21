"""
HR Agent - STANDARD OPENAI FUNCTION CALLING 
==========================================================
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
            "name": "request_w2_form",
            "description": "Request W-2 tax form for the employee",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "Employee ID or first name"},
                    "year": {"type": "integer", "description": "Tax year (e.g., 2025)"}
                },
                "required": ["employee_id", "year"]
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

CRITICAL FORMATTING RULE:
NEVER create markdown links like [here](#) or [download](#) or [click here](#) in your responses.
The system will automatically add download buttons and links when needed - you should NEVER create them yourself.

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

EXAMPLE 2 - 401K (BRIEF THEN DETAILED):
User: "What are my 401k options?"
You: "We offer a 401(k) plan with a 6% company match. Would you like to know more about the matching details, vesting schedule, contribution limits, or investment options? Or I can help you get started with enrollment."

User: "Tell me about the match"
You: "The company matches 100% on the first 6% you contribute. So if you contribute 6% of your salary, the company adds another 6% - that's free money! For example, on your salary that would be about $3,716/year from the company."

User: "What about vesting?"
You: "Your contributions are 100% vested immediately (they're always yours). The company match vests at 20% per year over 5 years, so you'll be fully vested after 5 years of employment."

User: "I'd like to enroll"
You: [IMMEDIATELY call escalate_to_hr with subject="401(k) Enrollment Request"]
You: "Here's the email to HR: [show email_draft]"

WRONG BEHAVIOR (NEVER DO THIS):
User: "Yes I'd like to enroll"
You: "What would you like to enroll in?" ← FORBIDDEN! You were JUST talking about 401k!

EXAMPLE 3 - HEALTH INSURANCE (SHOW ALL DETAILS):
User: "What are my health insurance options?"
You: [Call get_health_insurance_plans]
You: "Here are your health insurance options:

**Blue Shield PPO Gold**
- Employee Cost: $250/month
- Family Cost: $650/month
- Deductible: $500 (individual), $1000 (family)
- Out-of-Pocket Max: $3000 (individual), $6000 (family)
- Coverage: Nationwide network, no referrals needed, covers 80% after deductible

[Continue with other plans...]"

WRONG BEHAVIOR (NEVER DO THIS):
User: "What are my health insurance options?"
You: "Here are the plans: Blue Shield PPO, Kaiser HMO... but I don't have cost details" ← FORBIDDEN! The costs ARE in the tool response!

EXAMPLE 4 - W-2 REQUEST (SAY NOTHING ABOUT LINKS):
User: "Can I get my W-2?"
You: [IMMEDIATELY call request_w2_form with year=2025]
You: "Your W-2 tax document for 2025 is ready."

CORRECT - Just say it's ready. The download button appears automatically below your message.

WRONG BEHAVIOR (NEVER DO THIS):
User: "Can I get my W-2?"
You: "Your W-2 for 2025 is ready! You can download it [here](#)" ← FORBIDDEN! Don't add links!
OR
You: "Your W-2 for 2025 is ready! Download it here" ← FORBIDDEN! Don't say "download"!
OR
You: "For which tax year?" ← FORBIDDEN! Assume 2025!

SIMPLE RULES:
1. Answer questions directly
2. Use tools to get data (salary, PTO, health plans, W-2)
3. When user wants to DO something (enroll, take PTO, etc.), use email_manager or escalate_to_hr
4. Always show the email_draft from tool responses
5. When user says "yes" to your offer, DO IT - don't ask again
6. **HEALTH INSURANCE:** When showing health insurance plans, ALWAYS include ALL details: name, type, employee cost, family cost, deductible, out-of-pocket max, and coverage details. NEVER say you don't have the information - it's in the tool response!
7. **401(k) RETIREMENT PLAN - CONVERSATIONAL APPROACH:**
   
   **Initial Response (BRIEF):**
   "We offer a 401(k) plan with a 6% company match. Would you like to know more about the matching details, vesting schedule, contribution limits, or investment options? Or I can help you get started with enrollment."
   
   **Follow-Up Details (if asked):**
   - **Match/Matching:** Company matches 100% on first 6% you contribute (free money!)
   - **Vesting:** Your contributions are 100% vested immediately. Company match vests 20% per year over 5 years (100% after 5 years)
   - **Contribution limits:** $23,500/year if under 50, $31,000/year if 50+ (includes catch-up)
   - **Investment options:** Target-date funds, S&P 500 index funds, international funds, bond funds (managed by Fidelity)
   - **How to enroll/change:** Can enroll or change contribution anytime through payroll
   
   Answer ONLY what they ask about. Don't dump all info at once.

8. **W-2 TAX FORMS - INSTANT ACCESS:**
   When user asks for W-2 (without specifying year), automatically assume they want 2025 (the most recent tax year).
   DO NOT ask "which year?" - just use 2025.
   Call request_w2_form with year=2025.
   After calling the tool, respond with EXACTLY: "Your W-2 tax document for 2025 is ready."
   
   CRITICAL - DO NOT:
   - Add the word "download" to your response
   - Add any links like [here](#) or [download](#) 
   - Say "click here" or "available here"
   - Add ANY brackets [ ] to your response
   - The system will automatically add a download button - you don't need to mention it!

BE DIRECT. CALL TOOLS. REMEMBER CONTEXT."""


# ================================================================
# TOOL EXECUTION
# ================================================================

def execute_function(function_name: str, arguments: dict, employees_df: pd.DataFrame, health_plans_df: pd.DataFrame) -> str:
    """Execute a function call and return the result - ALWAYS returns valid JSON"""
    
    print(f"\n🔧 EXECUTING: {function_name}({arguments})")
    
    try:
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
                    'name': plan.get('Plan Name', 'Unknown'),
                    'type': plan.get('Plan Type', 'Unknown'),
                    'employee_cost': plan.get('Monthly Cost Employee', plan.get('Employee Monthly Cost', 'Unknown')),
                    'family_cost': plan.get('Monthly Cost Family', plan.get('Family Monthly Cost', 'Unknown')),
                    'deductible_individual': plan.get('Deductible Individual', plan.get('Deductible', 'Unknown')),
                    'deductible_family': plan.get('Deductible Family', 'Unknown'),
                    'oop_max_individual': plan.get('Out of Pocket Max Individual', 'Unknown'),
                    'oop_max_family': plan.get('Out of Pocket Max Family', 'Unknown'),
                    'coverage_details': plan.get('Coverage Details', 'Unknown')
                })
            return json.dumps({'success': True, 'plans': plans})
        
        elif function_name == "request_w2_form":
            employee = find_employee(employees_df, arguments['employee_id'])
            if employee is None:
                return json.dumps({'success': False, 'error': 'Employee not found'})
            
            employee_name = employee.get('First Name', 'Unknown')
            year = arguments.get('year', 2025)
            
            # Backend will detect "W-2" and add download link automatically
            return json.dumps({
                'success': True,
                'action': 'request_w2',
                'employee_name': employee_name,
                'year': year,
                'message': f"W-2 tax document for {year} is ready"
            })
        
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
        
        else:
            return json.dumps({'success': False, 'error': 'Unknown function'})
    
    except Exception as e:
        print(f"❌ ERROR in execute_function: {function_name}, {e}")
        import traceback
        traceback.print_exc()
        return json.dumps({'success': False, 'error': f'System error: {str(e)}'})


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
        
        if len(conversation) > 20:
            conversation = conversation[-20:]
            self.employee_conversations[employee_id] = conversation
        
        try:
            print(f"\n{'='*60}")
            print(f"EMPLOYEE: {employee_id}, MESSAGE: {message}")
            print(f"{'='*60}\n")
            
            # Tell AI who the employee is
            system_prompt_with_context = f"""{SYSTEM_PROMPT}

IMPORTANT CONTEXT:
You are currently helping employee: {employee_id}
When calling tools like get_pto_balance, get_employee_salary, request_w2_form, etc., ALWAYS use "{employee_id}" as the employee_id parameter.
The user doesn't need to tell you their ID - you already know it's {employee_id}."""
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": system_prompt_with_context}] + conversation,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            if not tool_calls:
                assistant_message = response_message.content
                conversation.append({'role': 'assistant', 'content': assistant_message})
                print(f"\n📤 RESPONSE: {assistant_message}\n")
                return {'success': True, 'response': assistant_message}
            
            conversation.append(response_message.model_dump())
            
            for tool_call in tool_calls:
                try:
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
                    
                except Exception as e:
                    print(f"❌ ERROR processing tool call: {e}")
                    conversation.append({
                        'role': 'tool',
                        'tool_call_id': tool_call.id,
                        'name': tool_call.function.name,
                        'content': json.dumps({'success': False, 'error': f'Tool execution failed: {str(e)}'})
                    })
            
            final_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": system_prompt_with_context}] + conversation,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            assistant_message = final_response.choices[0].message.content
            conversation.append({'role': 'assistant', 'content': assistant_message})
            
            print(f"\n📤 FINAL RESPONSE: {assistant_message}\n")
            
            return {'success': True, 'response': assistant_message}
            
        except Exception as e:
            import traceback
            print(f"\n❌ ERROR:")
            print(traceback.format_exc())
            
            return {
                'success': False,
                'response': f"I apologize, but I encountered an issue: {str(e)}",
                'error': str(e)
            }
