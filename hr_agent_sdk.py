"""
HR Agent SDK
A simple SDK for answering employee HR questions from a CSV database.
"""

import pandas as pd
import re
from typing import Optional, Dict, Any, List
from datetime import datetime


class HRDatabase:
    """Handles loading and querying the HR CSV database."""
    
    def __init__(self, csv_path: str):
        """
        Initialize the HR database.
        
        Args:
            csv_path: Path to the CSV file containing employee data
        """
        self.csv_path = csv_path
        self.df = None
        self.load_database()
    
    def load_database(self):
        """Load the CSV file into a pandas DataFrame."""
        try:
            self.df = pd.read_csv(self.csv_path)
            print(f"✓ Loaded HR database with {len(self.df)} employees")
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found at: {self.csv_path}")
        except Exception as e:
            raise Exception(f"Error loading CSV: {str(e)}")
    
    def get_employee_by_id(self, employee_id: str) -> Optional[pd.Series]:
        """
        Get employee data by ID.
        
        Args:
            employee_id: The employee ID to search for
            
        Returns:
            Employee data as a pandas Series, or None if not found
        """
        # Try both column name variations
        if 'EmployeeID' in self.df.columns:
            result = self.df[self.df['EmployeeID'] == employee_id]
        elif 'Employee ID' in self.df.columns:
            result = self.df[self.df['Employee ID'] == employee_id]
        else:
            return None
            
        if len(result) > 0:
            return result.iloc[0]
        return None
    
    def get_employee_by_name(self, first_name: str) -> Optional[pd.Series]:
        """
        Get employee data by first name.
        
        Args:
            first_name: The employee's first name
            
        Returns:
            Employee data as a pandas Series, or None if not found
        """
        result = self.df[self.df['First Name'].str.lower() == first_name.lower()]
        if len(result) > 0:
            return result.iloc[0]
        return None
    
    def update_employee(self, employee_id: str = None, first_name: str = None, 
                       updates: Dict[str, Any] = None) -> bool:
        """
        Update employee data in the database
        
        Args:
            employee_id: Employee ID to update
            first_name: Or employee first name to update
            updates: Dictionary of field names and new values
            
        Returns:
            True if update successful, False otherwise
        """
        if updates is None or (employee_id is None and first_name is None):
            return False
        
        # Find the employee
        if employee_id:
            # Try both column name variations
            if 'EmployeeID' in self.df.columns:
                mask = self.df['EmployeeID'] == employee_id
            elif 'Employee ID' in self.df.columns:
                mask = self.df['Employee ID'] == employee_id
            else:
                return False
        else:
            mask = self.df['First Name'].str.lower() == first_name.lower()
        
        if not mask.any():
            return False
        
        # Update the fields
        for field, value in updates.items():
            if field in self.df.columns:
                self.df.loc[mask, field] = value
        
        # Save to CSV
        try:
            self.df.to_csv(self.csv_path, index=False)
            print(f"✓ Updated employee data and saved to {self.csv_path}")
            # Reload the dataframe to ensure fresh data
            self.load_database()
            return True
        except Exception as e:
            print(f"✗ Error saving updates: {e}")
            return False
    
    def save_database(self) -> bool:
        """
        Save the current database state to CSV
        
        Returns:
            True if save successful, False otherwise
        """
        try:
            self.df.to_csv(self.csv_path, index=False)
            return True
        except Exception as e:
            print(f"✗ Error saving database: {e}")
            return False


class QueryParser:
    """Parses natural language questions and extracts intent and entities."""
    
    # Define question patterns and their corresponding intents
    PATTERNS = {
        'salary': [
            r'what.*salary',
            r'how much.*make',
            r'how much.*paid',
            r'my.*salary',
            r'salary.*is'
        ],
        'days_off': [
            r'days off',
            r'vacation.*left',
            r'vacation.*remaining',
            r'time off',
            r'pto',
            r'leave.*remaining'
        ],
        'bonus': [
            r'bonus',
            r'what.*bonus',
            r'bonus percentage',
            r'bonus %'
        ],
        'work_location': [
            r'work.*person',
            r'on-site',
            r'onsite',
            r'remote',
            r'work.*office',
            r'where.*work',
            r'what.*town',
            r'which.*town',
            r'my.*town',
            r'what.*city',
            r'which.*city',
            r'my.*city',
            r'where.*located',
            r'my.*location',
            r'where.*live',
            r'where.*i.*live',
            r'my.*home',
            r'home.*town',
            r'home.*city',
            r'based.*in',
            r'living.*in'
        ],
        'team': [
            r'what.*team',
            r'which.*team',
            r'my.*team'
        ],
        'manager': [
            r'senior management',
            r'manager',
            r'who.*manager'
        ],
        'start_date': [
            r'start date',
            r'when.*start',
            r'hire date',
            r'joined'
        ],
        'schedule_call': [
            r'schedule.*call',
            r'book.*call',
            r'set.*up.*call',
            r'schedule.*meeting',
            r'book.*meeting',
            r'set.*up.*meeting',
            r'arrange.*call',
            r'arrange.*meeting',
            r'calendar',
            r'appointment',
            r'book.*time',
            r'schedule.*time',
            r'when.*available',
            r'availability',
            r'when.*can.*meet',
            r'when.*can.*talk',
            r'when.*can.*call',
            r'when.*free',
            r'free.*time',
            r'available.*time',
            r'set.*call',
            r'setup.*call',
            r'talk.*to.*hr',
            r'speak.*with.*hr',
            r'meet.*with.*hr',
            r'hr.*available',
            r'hr.*availability',
            r'available.*slot',
            r'free.*slot',
            r'time.*slot'
        ],
        'email_hr_request': [
            r'can.*i.*take',
            r'is.*there.*way',
            r'how.*can.*i.*get',
            r'need.*to.*request',
            r'want.*to.*request',
            r'need.*help.*with',
            r'need.*assistance',
            r'request.*for',
            r'apply.*for',
            r'extra.*day',
            r'more.*days.*off',
            r'additional.*pto',
            r'exception.*to',
            r'special.*request',
            r'can.*you.*help.*me',
            r'is.*it.*possible',
            r'would.*it.*be.*possible'
        ],
        'health_insurance': [
            r'health.*insurance',
            r'medical.*insurance',
            r'health.*plan',
            r'insurance.*option',
            r'health.*benefit',
            r'medical.*plan',
            r'health.*coverage',
            r'insurance.*cost',
            r'health.*care',
            r'medical.*benefit',
            r'hmo',
            r'ppo',
            r'hdhp',
            r'deductible',
            r'premium'
        ],
        'remote_response': [
            r'^remote$',
            r'^remotely$',
            r'^remote work',
            r'^work.*remote',
            r'i.*ll.*remote',
            r'i.*ll.*work.*remote',
            r'^onsite$',
            r'^on-site$',
            r'^on site$',
            r'^office$',
            r'i.*ll.*onsite',
            r'i.*ll.*office',
            r'at.*office',
            r'in.*office'
        ],
        'w2': [
            r'w-?2',
            r'tax.*form',
            r'tax.*document',
            r'wage.*statement',
            r'tax.*statement'
        ],
        'update_address': [
            r'change.*address',
            r'update.*address',
            r'new address',
            r'move.*to'
        ],
        'update_info': [
            r'change.*my',
            r'update.*my',
            r'modify.*my',
            r'edit.*my',
            r'mov(?:e|ed|ing)\s+to',
            r'relocated\s+to',
            r'transferred\s+to',
            r'promoted',
            r'reassigned',
            r'update.*that.*to',
            r'change.*that.*to',
            r'update.*it.*to',
            r'change.*it.*to',
            r'set.*to',
            r'make.*it'
        ]
    }
    
    @classmethod
    def parse(cls, question: str) -> str:
        """
        Parse a natural language question and return the intent.
        
        Args:
            question: The user's question
            
        Returns:
            The identified intent (e.g., 'salary', 'days_off')
        """
        question_lower = question.lower()
        
        for intent, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    return intent
        
        return 'unknown'


class HRAgent:
    """Main HR Agent that answers employee questions."""
    
    def __init__(self, csv_path: str, health_plans_df=None):
        """
        Initialize the HR Agent.
        
        Args:
            csv_path: Path to the CSV file containing employee data
            health_plans_df: Optional DataFrame with health insurance plans
        """
        self.database = HRDatabase(csv_path)
        self.parser = QueryParser()
        self.health_plans = health_plans_df
    
    def answer_question(self, question: str, employee_id: Optional[str] = None, 
                       first_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Answer an HR question for a specific employee.
        
        Args:
            question: The natural language question
            employee_id: The employee's ID (optional)
            first_name: The employee's first name (optional)
            
        Returns:
            Dictionary with 'answer', 'intent', and 'raw_data' keys
        """
        # Get employee data
        if employee_id:
            employee = self.database.get_employee_by_id(employee_id)
        elif first_name:
            employee = self.database.get_employee_by_name(first_name)
        else:
            return {
                'answer': 'Please provide either an employee_id or first_name.',
                'intent': 'error',
                'raw_data': None
            }
        
        if employee is None:
            return {
                'answer': 'Employee not found in the database.',
                'intent': 'error',
                'raw_data': None
            }
        
        # Parse the question
        intent = self.parser.parse(question)
        
        # Generate answer based on intent
        answer = self._generate_answer(intent, employee, question)
        
        return {
            'answer': answer,
            'intent': intent,
            'raw_data': employee.to_dict()
        }
    
    def _generate_answer(self, intent: str, employee: pd.Series, question: str = "") -> str:
        """
        Generate a natural language answer based on intent and employee data.
        
        Args:
            intent: The identified intent
            employee: The employee's data
            
        Returns:
            Natural language answer string
        """
        name = employee['First Name']
        
        if intent == 'salary':
            salary = employee['Salary']
            return f"{name}'s salary is ${salary:,.2f} per year."
        
        elif intent == 'days_off':
            days = employee['Days Off Remaining']
            return f"{name} has {days} days off remaining this year."
        
        elif intent == 'bonus':
            bonus_pct = employee['Bonus %']
            return f"{name}'s bonus percentage is {bonus_pct}%."
        
        elif intent == 'work_location':
            # Check if this is asking about a policy change that needs HR approval
            question_lower = question.lower()
            needs_hr_approval = any([
                'can i' in question_lower and 'move' in question_lower,
                'can i' in question_lower and 'relocate' in question_lower,
                'can i' in question_lower and 'work remote' in question_lower,
                'can i' in question_lower and 'work from' in question_lower,
                'permission' in question_lower and ('move' in question_lower or 'remote' in question_lower),
                'allowed to' in question_lower and ('move' in question_lower or 'remote' in question_lower)
            ])
            
            if needs_hr_approval:
                return f"HYBRID_REQUEST:{question}"
            
            # Check for both 'Location' and 'Town' column names
            if 'Location' in employee.index:
                location = employee['Location']
            elif 'Town' in employee.index:
                location = employee['Town']
            else:
                location = None
            
            # Check if they're asking about where they live vs where they work
            question_lower = question.lower()
            asking_about_living = any(word in question_lower for word in ['live', 'home', 'residing', 'based'])
            
            # Assuming if Location/Town is provided, they work on-site in that location
            if pd.notna(location) and location != '':
                if asking_about_living:
                    return f"{name} lives in {location}."
                else:
                    return f"{name} works on-site in {location}."
            else:
                return f"{name}'s location information is not available."
        
        elif intent == 'team':
            team = employee['Team']
            return f"{name} is on the {team} team."
        
        elif intent == 'manager':
            is_senior = employee['Senior Management']
            if is_senior == True or is_senior == 'True' or is_senior == 'Yes':
                return f"{name} is part of senior management."
            else:
                return f"{name} is not part of senior management."
        
        elif intent == 'start_date':
            start_date = employee['Start Date']
            return f"{name} started on {start_date}."
        
        elif intent == 'w2':
            # Return a special response that the backend will handle
            return f"W2_REQUEST:{name}"
        
        elif intent == 'schedule_call':
            # Return a special response that the frontend will handle
            return f"SCHEDULE_CALL_REQUEST:{name}"
        
        elif intent == 'health_insurance':
            # Return health insurance options
            if self.health_plans is not None and len(self.health_plans) > 0:
                plans_list = []
                
                for idx, plan in self.health_plans.iterrows():
                    plan_text = (
                        f"{plan['Plan Name']} ({plan['Plan Type']})\n"
                        f"  Employee: {plan['Monthly Cost Employee']}/month\n"
                        f"  Family: {plan['Monthly Cost Family']}/month\n"
                        f"  Deductible: {plan['Deductible Individual']}\n"
                    )
                    plans_list.append(plan_text)
                
                response = "We offer 4 health insurance plans:\n\n" + "\n".join(plans_list)
                response += "\nWould you like more details about a specific plan?"
                return response
            else:
                return "I don't have health insurance information loaded. Let me connect you with HR to discuss your benefits options."
        
        elif intent == 'email_hr_request':
            # Return a special response to trigger email draft
            return f"EMAIL_HR_REQUEST:{question}"
        
        elif intent in ['update_address', 'update_info']:
            # Check if this is a complex request that needs HR approval
            # e.g., "Can I move and work remote?" - answerable but needs HR
            question_lower = question.lower()
            needs_hr_approval = any([
                'can i' in question_lower and ('move' in question_lower or 'relocate' in question_lower),
                'can i' in question_lower and 'work remote' in question_lower,
                'permission' in question_lower,
                'allowed to' in question_lower,
                'policy' in question_lower and ('remote' in question_lower or 'work from' in question_lower),
                'approval' in question_lower
            ])
            
            if needs_hr_approval:
                # This is both informational AND needs HR approval
                return f"HYBRID_REQUEST:{question}"
            
            # Try to extract update information from the question
            # Try to extract update information from the question
            update_info = self._parse_update_request(question, employee)
            
            if update_info:
                # Check if this is a location update - ask about remote status
                location_col = 'Location' if 'Location' in employee.index else 'Town'
                if location_col in update_info:
                    # Return a special response asking about remote status
                    new_location = update_info[location_col]
                    return f"LOCATION_UPDATE_REQUEST:{new_location}"
                
                # For non-location updates, process immediately
                # Perform the update
                success = self.database.update_employee(
                    employee_id=emp_id,
                    first_name=employee['First Name'],
                    updates=update_info
                )
                
                if success:
                    updates_str = ', '.join([f"{k} to {v}" for k, v in update_info.items()])
                    return f"Successfully updated {updates_str} for {name}."
                else:
                    return f"Sorry, I couldn't update your information. Please try again."
            else:
                # Couldn't parse - ask for clarification
                return f"I'd like to help you update your information. Please tell me what you'd like to change. For example: 'Change my address to Miami' or 'Update my team to Engineering'."
        
        else:
            # Unknown intent - offer to email HR
            return f"EMAIL_HR_UNKNOWN:{question}"
    
    def _parse_update_request(self, question: str, employee: pd.Series) -> Optional[Dict[str, Any]]:
        """
        Parse a natural language update request to extract field and value.
        
        Args:
            question: The update request
            employee: Employee data
            
        Returns:
            Dictionary of field names to new values, or None if couldn't parse
        """
        import re
        question_lower = question.lower()
        updates = {}
        
        # Determine which column name to use (Location or Town)
        location_col = 'Location' if 'Location' in employee.index else 'Town'
        
        # Pattern: "update/change that/it to [location]" (contextual - assume Location/Town)
        contextual_match = re.search(r'(?:update|change|set|make)\s+(?:that|it)\s+to\s+([a-zA-Z\s]+?)(?:\.|$|,)', question_lower)
        if contextual_match:
            value = contextual_match.group(1).strip().title()
            # Default to Location/Town for contextual updates
            updates[location_col] = value
        
        # Pattern: "move to [location]" or "moving to [location]"
        move_match = re.search(r'mov(?:e|ing)\s+to\s+([a-zA-Z\s]+?)(?:\.|$|,|\sand\s)', question_lower)
        if move_match:
            location = move_match.group(1).strip().title()
            updates[location_col] = location
        
        # Pattern: "change/update [field] to [value]"
        change_patterns = [
            r'(?:change|update|set|modify)\s+(?:my\s+)?(?:address|town|city|location)\s+to\s+([a-zA-Z\s]+?)(?:\.|$|,)',
            r'(?:change|update|set|modify)\s+(?:my\s+)?team\s+to\s+([a-zA-Z\s]+?)(?:\.|$|,)',
            r'(?:change|update|set|modify)\s+(?:my\s+)?salary\s+to\s+([0-9,]+)',
            r'(?:change|update|set|modify)\s+(?:my\s+)?bonus\s+to\s+([0-9.]+)',
        ]
        
        for pattern in change_patterns:
            match = re.search(pattern, question_lower)
            if match:
                value = match.group(1).strip()
                
                # Determine which field based on pattern
                if 'address' in pattern or 'town' in pattern or 'city' in pattern or 'location' in pattern:
                    updates[location_col] = value.title()
                elif 'team' in pattern:
                    updates['Team'] = value.title()
                elif 'salary' in pattern:
                    # Remove commas and convert to int
                    updates['Salary'] = int(value.replace(',', ''))
                elif 'bonus' in pattern:
                    updates['Bonus %'] = float(value)
        
        # Pattern: "relocated to [location]" or "transferred to [location]"
        reloc_match = re.search(r'(?:relocated|transferred|reassigned)\s+to\s+([a-zA-Z\s]+?)(?:\.|$|,)', question_lower)
        if reloc_match:
            location = reloc_match.group(1).strip().title()
            updates[location_col] = location
        
        return updates if updates else None
    
    def update_employee_data(self, employee_id: str = None, first_name: str = None,
                            field: str = None, new_value: Any = None) -> Dict[str, Any]:
        """
        Update employee data in the database
        
        Args:
            employee_id: Employee ID
            first_name: Or employee first name
            field: Field to update (e.g., 'Town', 'Salary')
            new_value: New value for the field
            
        Returns:
            Dictionary with success status and message
        """
        if field is None or new_value is None:
            return {
                'success': False,
                'message': 'Please specify what field to update and the new value.'
            }
        
        # Map common field names to actual column names
        field_mapping = {
            'address': 'Town',
            'town': 'Town',
            'city': 'Town',
            'salary': 'Salary',
            'bonus': 'Bonus %',
            'days off': 'Days Off Remaining',
            'pto': 'Days Off Remaining',
            'team': 'Team'
        }
        
        actual_field = field_mapping.get(field.lower(), field)
        
        success = self.database.update_employee(
            employee_id=employee_id,
            first_name=first_name,
            updates={actual_field: new_value}
        )
        
        if success:
            return {
                'success': True,
                'message': f'Successfully updated {field} to {new_value}.'
            }
        else:
            return {
                'success': False,
                'message': f'Failed to update {field}. Please try again.'
            }
    
    def get_all_employees(self) -> List[Dict]:
        """
        Get a list of all employees (useful for testing/debugging).
        
        Returns:
            List of employee dictionaries
        """
        return self.database.df.to_dict('records')


# Example usage
if __name__ == "__main__":
    # Initialize the agent with your CSV file path
    agent = HRAgent("path/to/your/hr_data.csv")
    
    # Ask questions using employee ID
    result = agent.answer_question(
        "How many days off do I still have?",
        employee_id="EMP001"
    )
    print(f"Answer: {result['answer']}")
    print(f"Intent: {result['intent']}\n")
    
    # Ask questions using first name
    result = agent.answer_question(
        "What's my salary?",
        first_name="John"
    )
    print(f"Answer: {result['answer']}")
    print(f"Intent: {result['intent']}\n")
    
    # Different question types
    questions = [
        "What is my bonus?",
        "Do I have to work in person?",
        "What team am I on?"
    ]
    
    for q in questions:
        result = agent.answer_question(q, employee_id="EMP001")
        print(f"Q: {q}")
        print(f"A: {result['answer']}\n")
