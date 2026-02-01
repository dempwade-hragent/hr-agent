"""
Interactive HR Chatbot
A simple command-line interface for the HR Agent SDK
"""

from hr_agent_sdk import HRAgent
import sys

def print_header():
    print("\n" + "="*60)
    print("        HR ASSISTANT CHATBOT")
    print("="*60)
    print("\nI can answer questions about:")
    print("  • Salary and compensation")
    print("  • Days off / PTO / Vacation time")
    print("  • Bonus percentage")
    print("  • Work location (on-site/remote)")
    print("  • Team assignment")
    print("  • Management status")
    print("  • Start date")
    print("\nType 'exit' or 'quit' to end the conversation")
    print("Type 'switch' to change employee")
    print("="*60 + "\n")

def get_employee_info():
    """Get employee identifier from user"""
    print("\nHow would you like to identify yourself?")
    print("1. Employee ID")
    print("2. First Name")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        employee_id = input("Enter your Employee ID: ").strip()
        return {'employee_id': employee_id}
    elif choice == "2":
        first_name = input("Enter your First Name: ").strip()
        return {'first_name': first_name}
    else:
        print("Invalid choice. Please try again.")
        return get_employee_info()

def main():
    # Check if CSV path is provided as command line argument
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        csv_path = input("Enter path to HR CSV file (or press Enter for 'sample_hr_data.csv'): ").strip()
        if not csv_path:
            csv_path = "sample_hr_data.csv"
    
    try:
        agent = HRAgent(csv_path)
    except FileNotFoundError:
        print(f"\n❌ Error: Could not find CSV file at '{csv_path}'")
        print("Please check the path and try again.")
        return
    except Exception as e:
        print(f"\n❌ Error loading database: {e}")
        return
    
    print_header()
    
    # Get initial employee info
    employee_info = get_employee_info()
    
    print("\n" + "="*60)
    print("Great! You can now ask me questions.")
    print("="*60 + "\n")
    
    while True:
        question = input("You: ").strip()
        
        if not question:
            continue
            
        if question.lower() in ['exit', 'quit', 'bye']:
            print("\n👋 Goodbye! Have a great day!")
            break
            
        if question.lower() == 'switch':
            print("\n" + "="*60)
            employee_info = get_employee_info()
            print("="*60 + "\n")
            continue
        
        # Get answer from agent
        result = agent.answer_question(question, **employee_info)
        
        # Print response
        if result['intent'] == 'error':
            print(f"\n❌ {result['answer']}\n")
        elif result['intent'] == 'unknown':
            print(f"\n🤔 {result['answer']}\n")
        else:
            print(f"\n✓ {result['answer']}\n")

if __name__ == "__main__":
    main()
