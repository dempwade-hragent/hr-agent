"""
Example usage of the HR Agent SDK
"""

from hr_agent_sdk import HRAgent

def main():
    # Initialize the HR Agent with your CSV file
    print("=== HR Agent SDK Demo ===\n")
    
    # Use the sample data or replace with your actual CSV path
    agent = HRAgent("sample_hr_data.csv")
    
    print("Example 1: Query by Employee ID")
    print("-" * 50)
    result = agent.answer_question(
        "How many days off do I still have?",
        employee_id="EMP001"
    )
    print(f"Question: How many days off do I still have?")
    print(f"Answer: {result['answer']}")
    print(f"Detected Intent: {result['intent']}\n")
    
    print("Example 2: Query by First Name")
    print("-" * 50)
    result = agent.answer_question(
        "What's my salary?",
        first_name="Sarah"
    )
    print(f"Question: What's my salary?")
    print(f"Answer: {result['answer']}")
    print(f"Detected Intent: {result['intent']}\n")
    
    print("Example 3: Multiple Questions for Same Employee")
    print("-" * 50)
    questions = [
        "What is my bonus?",
        "Do I have to work in person?",
        "What team am I on?",
        "When did I start?",
        "Am I a senior manager?"
    ]
    
    for question in questions:
        result = agent.answer_question(question, employee_id="EMP003")
        print(f"Q: {question}")
        print(f"A: {result['answer']}\n")
    
    print("Example 4: Testing Different Phrasings")
    print("-" * 50)
    variations = [
        "How many more days off do I have this year?",
        "What's my vacation time remaining?",
        "How much PTO do I have left?"
    ]
    
    for question in variations:
        result = agent.answer_question(question, first_name="Emily")
        print(f"Q: {question}")
        print(f"A: {result['answer']}\n")
    
    print("Example 5: Accessing Raw Employee Data")
    print("-" * 50)
    result = agent.answer_question(
        "What's my bonus?",
        employee_id="EMP002"
    )
    print(f"Answer: {result['answer']}")
    print(f"\nRaw employee data:")
    for key, value in result['raw_data'].items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
