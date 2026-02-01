# HR Agent SDK

A simple Python SDK for building HR chatbots that can answer employee questions from a CSV database.

## Features

- 📊 **CSV Database Integration**: Load and query employee data from CSV files
- 🤖 **Natural Language Processing**: Parse questions like "How many days off do I have?"
- 🎯 **Intent Recognition**: Automatically detect what information the user is asking for
- 📝 **Multiple Query Types**: Support for salary, PTO, bonus, location, team, and more
- 🔍 **Flexible Search**: Query by Employee ID or First Name

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your CSV file has the following columns:
   - First Name
   - Gender
   - Start Date
   - Last Login Time
   - Salary
   - Bonus %
   - Senior Management
   - Team
   - Days Off Remaining
   - Town
   - EmployeeID

## Quick Start

```python
from hr_agent_sdk import HRAgent

# Initialize the agent with your CSV file
agent = HRAgent("path/to/your/hr_data.csv")

# Ask a question using employee ID
result = agent.answer_question(
    "How many days off do I still have?",
    employee_id="EMP001"
)
print(result['answer'])

# Ask a question using first name
result = agent.answer_question(
    "What's my salary?",
    first_name="John"
)
print(result['answer'])
```

## Supported Question Types

The SDK can handle the following types of questions:

### Salary Questions
- "What's my salary?"
- "How much do I make?"
- "What am I paid?"

### Days Off / PTO
- "How many days off do I still have?"
- "What's my vacation time remaining?"
- "How much PTO do I have left?"

### Bonus Questions
- "What is my bonus?"
- "What's my bonus percentage?"

### Work Location
- "Do I have to work in person?"
- "Am I on-site or remote?"
- "Where do I work?"

### Team Information
- "What team am I on?"
- "Which team do I work for?"

### Management Status
- "Am I in senior management?"
- "Am I a manager?"

### Start Date
- "When did I start?"
- "What's my hire date?"

## API Reference

### HRAgent

The main class for the HR Agent.

#### `__init__(csv_path: str)`
Initialize the HR Agent with a CSV database.

**Parameters:**
- `csv_path` (str): Path to the CSV file containing employee data

#### `answer_question(question: str, employee_id: Optional[str] = None, first_name: Optional[str] = None) -> Dict[str, Any]`
Answer an HR question for a specific employee.

**Parameters:**
- `question` (str): The natural language question
- `employee_id` (str, optional): The employee's ID
- `first_name` (str, optional): The employee's first name

**Returns:**
Dictionary with the following keys:
- `answer` (str): Natural language answer
- `intent` (str): Detected intent (e.g., 'salary', 'days_off')
- `raw_data` (dict): Raw employee data from the database

**Example:**
```python
result = agent.answer_question(
    "What's my bonus?",
    employee_id="EMP001"
)
print(result['answer'])  # "John's bonus percentage is 10%."
print(result['intent'])  # "bonus"
print(result['raw_data'])  # Full employee record
```

#### `get_all_employees() -> List[Dict]`
Get a list of all employees in the database.

**Returns:**
List of dictionaries, each containing employee data

## Advanced Usage

### Accessing Raw Employee Data

```python
result = agent.answer_question(
    "What's my salary?",
    employee_id="EMP001"
)

# Get the formatted answer
print(result['answer'])

# Access raw data for custom processing
employee_data = result['raw_data']
print(f"Salary: ${employee_data['Salary']}")
print(f"Team: {employee_data['Team']}")
```

### Building a Chatbot Interface

```python
from hr_agent_sdk import HRAgent

agent = HRAgent("hr_data.csv")

def chatbot():
    print("HR Chatbot - Type 'exit' to quit")
    employee_id = input("Enter your Employee ID: ")
    
    while True:
        question = input("\nYou: ")
        if question.lower() == 'exit':
            break
            
        result = agent.answer_question(question, employee_id=employee_id)
        print(f"Bot: {result['answer']}")

chatbot()
```

### Extending the SDK

You can add new question patterns by extending the `QueryParser.PATTERNS` dictionary:

```python
from hr_agent_sdk import QueryParser

# Add custom patterns
QueryParser.PATTERNS['custom_intent'] = [
    r'your custom regex pattern',
    r'another pattern'
]
```

Then add handling in `HRAgent._generate_answer()`:

```python
elif intent == 'custom_intent':
    # Your custom logic here
    return f"Custom answer for {name}"
```

## Testing

Run the example script to test the SDK:

```bash
python example_usage.py
```

This will demonstrate various query types using the sample data.

## CSV Format

Your CSV file should follow this format:

```csv
First Name,Gender,Start Date,Last Login Time,Salary,Bonus %,Senior Management,Team,Days Off Remaining,Town,EmployeeID
John,Male,2020-01-15,2024-01-28 14:30,85000,10,False,Engineering,12,San Francisco,EMP001
Sarah,Female,2019-03-22,2024-01-29 09:15,95000,15,True,Product,8,New York,EMP002
```

## Error Handling

The SDK provides clear error messages:

```python
# Employee not found
result = agent.answer_question("What's my salary?", employee_id="INVALID")
# Returns: {'answer': 'Employee not found in the database.', 'intent': 'error', ...}

# No employee identifier provided
result = agent.answer_question("What's my salary?")
# Returns: {'answer': 'Please provide either an employee_id or first_name.', 'intent': 'error', ...}

# Unknown question type
result = agent.answer_question("What's the weather?", employee_id="EMP001")
# Returns helpful message about supported question types
```

## Future Enhancements

Potential improvements for the SDK:

- [ ] Add fuzzy name matching for typos
- [ ] Support for more complex queries (e.g., "Who has the most PTO?")
- [ ] Integration with LLMs for better natural language understanding
- [ ] Multi-language support
- [ ] Database backend support (SQL, MongoDB, etc.)
- [ ] REST API wrapper
- [ ] Authentication and authorization
- [ ] Logging and analytics

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
