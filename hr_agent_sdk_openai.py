"""
HR Agent SDK - OpenAI Agents Version
=====================================

REPLACES: hr_agent_sdk.py (regex-based)

NO MORE:
- Regex pattern matching
- Manual intent detection
- If/else chains

NOW:
- OpenAI Assistants API
- Automatic tool selection
- Stateful conversations
"""

from openai import OpenAI
import pandas as pd
import json
import time
from typing import Dict, Any, Optional
import os

api_key=os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key = api_key)  # Requires OPENAI_API_KEY environment variable


class HRAgentOpenAI:
    """HR Agent using OpenAI Assistants API"""
    
    def __init__(self, employees_df: pd.DataFrame, health_plans_df: Optional[pd.DataFrame] = None):
        """
        Initialize HR Agent with OpenAI Assistants API
        
        Args:
            employees_df: DataFrame with employee data
            health_plans_df: DataFrame with health insurance plans (optional)
        """
        self.employees_df = employees_df
        self.health_plans = health_plans_df
        
        # Create the assistant (agent)
        self.assistant = self._create_assistant()
        
        # Track active threads per employee
        self.active_threads = {}
        
        print(f"✅ OpenAI HR Agent initialized (Assistant ID: {self.assistant.id})")
    
    def _create_assistant(self):
        """Create the OpenAI assistant with all HR tools"""
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_employee_salary",
                    "description": "Get salary information for an employee. Use when asked about pay, compensation, or earnings.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "string",
                                "description": "Employee's ID number"
                            }
                        },
                        "required": ["employee_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_pto_balance",
                    "description": "Get remaining PTO (paid time off) days. Use when asked about vacation, days off, or PTO.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "string",
                                "description": "Employee's ID number"
                            }
                        },
                        "required": ["employee_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_bonus_info",
                    "description": "Get bonus percentage for an employee. Use when asked about bonuses or incentives.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "string",
                                "description": "Employee's ID number"
                            }
                        },
                        "required": ["employee_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_location",
                    "description": "Get the office location where an employee works.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "string",
                                "description": "Employee's ID number"
                            }
                        },
                        "required": ["employee_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_team_info",
                    "description": "Get the team/department an employee belongs to.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "string",
                                "description": "Employee's ID number"
                            }
                        },
                        "required": ["employee_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_manager_info",
                    "description": "Get information about an employee's manager.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "string",
                                "description": "Employee's ID number"
                            }
                        },
                        "required": ["employee_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_health_insurance_plans",
                    "description": "Get all available health insurance plans with costs and coverage details.",
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
                    "name": "generate_w2_request",
                    "description": "Create a request to generate a W-2 tax form for an employee.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "string",
                                "description": "Employee's ID number"
                            }
                        },
                        "required": ["employee_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "escalate_to_hr",
                    "description": "Draft an email to HR for requests that require human assistance or approval.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "string",
                                "description": "Employee's ID number"
                            },
                            "subject": {
                                "type": "string",
                                "description": "Email subject line"
                            },
                            "request": {
                                "type": "string",
                                "description": "Detailed description of the request"
                            }
                        },
                        "required": ["employee_id", "subject", "request"]
                    }
                }
            }
        ]
        
        assistant = client.beta.assistants.create(
            name="HR Assistant",
            instructions="""You are a helpful and professional HR assistant for company employees.

You help with:
- Salary and compensation information
- PTO/vacation balance inquiries
- Bonus information
- Office locations
- Team and manager information
- Health insurance plan comparisons
- W-2 tax form requests
- Escalating complex requests to HR

Guidelines:
- Always be friendly, professional, and concise
- Use the employee's name when you have it
- Format currency as $XX,XXX with commas
- When showing health plans, create a clear comparison
- If you cannot help directly, offer to escalate to HR
- Never make up information - only use data from tools
- Keep responses under 100 words unless asked for details

When using tools:
- Always pass the employee_id parameter
- Interpret results and format them nicely
- If a tool returns an error, apologize and offer alternatives
""",
            model="gpt-4o-mini",  # Cost-effective choice
            tools=tools
        )
        
        return assistant
    
    # ================================================================
    # TOOL IMPLEMENTATIONS (Called by OpenAI Agent)
    # ================================================================
    
    def get_employee_salary(self, employee_id: str) -> Dict[str, Any]:
        """Get salary for an employee"""
        try:
            employee = self.employees_df[self.employees_df['Employee ID'] == int(employee_id)].iloc[0]
            return {
                'success': True,
                'employee_id': employee_id,
                'name': employee['Employee Name'],
                'salary': int(employee['Salary'])
            }
        except (IndexError, KeyError):
            return {'success': False, 'error': 'Employee not found'}
    
    def get_pto_balance(self, employee_id: str) -> Dict[str, Any]:
        """Get PTO balance for an employee"""
        try:
            employee = self.employees_df[self.employees_df['Employee ID'] == int(employee_id)].iloc[0]
            return {
                'success': True,
                'employee_id': employee_id,
                'name': employee['Employee Name'],
                'days_remaining': int(employee['Days Off'])
            }
        except (IndexError, KeyError):
            return {'success': False, 'error': 'Employee not found'}
    
    def get_bonus_info(self, employee_id: str) -> Dict[str, Any]:
        """Get bonus percentage for an employee"""
        try:
            employee = self.employees_df[self.employees_df['Employee ID'] == int(employee_id)].iloc[0]
            return {
                'success': True,
                'employee_id': employee_id,
                'name': employee['Employee Name'],
                'bonus_percentage': int(employee['Bonus %'])
            }
        except (IndexError, KeyError):
            return {'success': False, 'error': 'Employee not found'}
    
    def get_location(self, employee_id: str) -> Dict[str, Any]:
        """Get employee's office location"""
        try:
            employee = self.employees_df[self.employees_df['Employee ID'] == int(employee_id)].iloc[0]
            return {
                'success': True,
                'employee_id': employee_id,
                'name': employee['Employee Name'],
                'location': employee['Location']
            }
        except (IndexError, KeyError):
            return {'success': False, 'error': 'Employee not found'}
    
    def get_team_info(self, employee_id: str) -> Dict[str, Any]:
        """Get employee's team/department"""
        try:
            employee = self.employees_df[self.employees_df['Employee ID'] == int(employee_id)].iloc[0]
            return {
                'success': True,
                'employee_id': employee_id,
                'name': employee['Employee Name'],
                'team': employee['Team']
            }
        except (IndexError, KeyError):
            return {'success': False, 'error': 'Employee not found'}
    
    def get_manager_info(self, employee_id: str) -> Dict[str, Any]:
        """Get employee's manager information"""
        try:
            employee = self.employees_df[self.employees_df['Employee ID'] == int(employee_id)].iloc[0]
            return {
                'success': True,
                'employee_id': employee_id,
                'name': employee['Employee Name'],
                'manager': employee['Manager']
            }
        except (IndexError, KeyError):
            return {'success': False, 'error': 'Employee not found'}
    
    def get_health_insurance_plans(self) -> Dict[str, Any]:
        """Get all health insurance plans"""
        if self.health_plans is None:
            return {'success': False, 'error': 'Health plans data not available'}
        
        plans = []
        for _, plan in self.health_plans.iterrows():
            plans.append({
                'name': plan['Plan Name'],
                'type': plan['Plan Type'],
                'employee_monthly': float(plan['Employee Cost (Monthly)']),
                'family_monthly': float(plan['Family Cost (Monthly)']),
                'deductible': float(plan['Deductible'])
            })
        
        return {'success': True, 'plans': plans}
    
    def generate_w2_request(self, employee_id: str) -> Dict[str, Any]:
        """Generate W-2 request (will be handled by backend)"""
        try:
            employee = self.employees_df[self.employees_df['Employee ID'] == int(employee_id)].iloc[0]
            return {
                'success': True,
                'action': 'w2_generation',
                'employee_id': employee_id,
                'name': employee['Employee Name'],
                'message': 'W-2 generation initiated. You will receive a download link shortly.'
            }
        except (IndexError, KeyError):
            return {'success': False, 'error': 'Employee not found'}
    
    def escalate_to_hr(self, employee_id: str, subject: str, request: str) -> Dict[str, Any]:
        """Escalate request to HR"""
        return {
            'success': True,
            'action': 'email_hr',
            'employee_id': employee_id,
            'subject': subject,
            'message': request,
            'recipient': 'hr@company.com',
            'status': 'draft_created'
        }
    
    # ================================================================
    # MAIN CHAT INTERFACE
    # ================================================================
    
    def chat(self, employee_id: str, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Main chat interface - handles everything automatically!
        
        NO REGEX! NO INTENT DETECTION!
        OpenAI agent decides what to do.
        
        Args:
            employee_id: Employee ID asking the question
            message: User's question
            session_id: Optional session ID for conversation continuity
        
        Returns:
            Response dict with answer and metadata
        """
        
        # Get or create thread for this session
        thread_id = self._get_or_create_thread(session_id or employee_id)
        
        # Add user message to thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=f"[Employee ID: {employee_id}] {message}"
        )
        
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant.id
        )
        
        # Wait for completion and handle tool calls
        response_text = self._wait_for_response(thread_id, run.id, employee_id)
        
        return {
            'success': True,
            'response': response_text,
            'method': 'openai_agents_sdk',
            'thread_id': thread_id
        }
    
    def _get_or_create_thread(self, session_id: str) -> str:
        """Get existing thread or create new one"""
        if session_id not in self.active_threads:
            thread = client.beta.threads.create()
            self.active_threads[session_id] = thread.id
        
        return self.active_threads[session_id]
    
    def _wait_for_response(self, thread_id: str, run_id: str, employee_id: str) -> str:
        """Wait for agent to complete and handle tool calls"""
        
        # Map function names to methods
        function_map = {
            'get_employee_salary': self.get_employee_salary,
            'get_pto_balance': self.get_pto_balance,
            'get_bonus_info': self.get_bonus_info,
            'get_location': self.get_location,
            'get_team_info': self.get_team_info,
            'get_manager_info': self.get_manager_info,
            'get_health_insurance_plans': self.get_health_insurance_plans,
            'generate_w2_request': self.generate_w2_request,
            'escalate_to_hr': self.escalate_to_hr,
        }
        
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            if run_status.status == 'requires_action':
                # Agent wants to call tools
                tool_outputs = []
                
                for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Execute the function
                    function_to_call = function_map.get(function_name)
                    if function_to_call:
                        result = function_to_call(**function_args)
                        tool_outputs.append({
                            'tool_call_id': tool_call.id,
                            'output': json.dumps(result)
                        })
                
                # Submit results back to agent
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run_id,
                    tool_outputs=tool_outputs
                )
            
            elif run_status.status == 'completed':
                # Get the response
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                return messages.data[0].content[0].text.value
            
            elif run_status.status in ['failed', 'cancelled', 'expired']:
                return f"I apologize, but I encountered an error processing your request. Please try again."
            
            time.sleep(0.5)
    
    def cleanup(self):
        """Clean up resources"""
        try:
            client.beta.assistants.delete(self.assistant.id)
            print(f"✅ Cleaned up assistant {self.assistant.id}")
        except Exception as e:
            print(f"⚠️  Error cleaning up: {e}")


# ================================================================
# BACKWARDS COMPATIBILITY (For gradual migration)
# ================================================================

class HRAgentSDK(HRAgentOpenAI):
    """
    Backwards compatible wrapper
    
    Provides same interface as old regex-based hr_agent_sdk.py
    but uses OpenAI Agents under the hood!
    """
    
    def answer_question(self, question: str, employee_id: str) -> str:
        """
        Legacy interface for compatibility
        
        Old code:
            agent = HRAgentSDK(df)
            response = agent.answer_question("What's my salary?", "1")
        
        Still works! Now powered by OpenAI Agents.
        """
        result = self.chat(employee_id, question)
        return result['response']
