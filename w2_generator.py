"""
W-2 Tax Form Generator
Generates realistic-looking W-2 PDFs for employees
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
import os
from datetime import datetime
import random
from typing import Optional, List, Dict, Any


class W2Generator:
    """Generates W-2 tax forms as PDFs"""
    
    def __init__(self, output_dir="tax_documents"):
        """
        Initialize W-2 generator
        
        Args:
            output_dir: Directory to save generated PDFs
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"✓ Created tax documents directory: {output_dir}")
    
    def generate_w2(self, employee_data: dict, year: int = 2024) -> str:
        """
        Generate a W-2 form for an employee
        
        Args:
            employee_data: Dictionary containing employee information
            year: Tax year (default: 2024)
            
        Returns:
            Path to the generated PDF file
        """
        first_name = employee_data.get('First Name', 'Unknown')
        employee_id = employee_data.get('Employee ID', employee_data.get('EmployeeID', 'UNKNOWN'))
        salary = employee_data.get('Salary', 0)
        # Check for both Location and Town column names
        town = employee_data.get('Location', employee_data.get('Town', 'Unknown City'))
        
        # Generate filename
        filename = f"{first_name}_W2_{year}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1*inch, height - 1*inch, f"Form W-2 - Wage and Tax Statement")
        c.setFont("Helvetica", 10)
        c.drawString(1*inch, height - 1.3*inch, f"Tax Year: {year}")
        
        # Draw border
        c.setStrokeColor(colors.HexColor("#5B8C85"))
        c.setLineWidth(2)
        c.rect(0.5*inch, height - 9*inch, 7.5*inch, 7.5*inch)
        
        # Employer Information Box
        y_pos = height - 2*inch
        c.setFont("Helvetica-Bold", 9)
        c.drawString(1*inch, y_pos, "Employer Information:")
        
        c.setFont("Helvetica", 8)
        y_pos -= 0.2*inch
        c.drawString(1*inch, y_pos, "Dempsey's Company Inc.")
        y_pos -= 0.15*inch
        c.drawString(1*inch, y_pos, "123 Business Avenue")
        y_pos -= 0.15*inch
        c.drawString(1*inch, y_pos, "New York, NY 10001")
        y_pos -= 0.15*inch
        c.drawString(1*inch, y_pos, f"EIN: 12-3456789")
        
        # Employee Information Box
        y_pos = height - 2*inch
        c.setFont("Helvetica-Bold", 9)
        c.drawString(4.5*inch, y_pos, "Employee Information:")
        
        c.setFont("Helvetica", 8)
        y_pos -= 0.2*inch
        c.drawString(4.5*inch, y_pos, f"{first_name}")
        y_pos -= 0.15*inch
        c.drawString(4.5*inch, y_pos, f"Employee ID: {employee_id}")
        y_pos -= 0.15*inch
        c.drawString(4.5*inch, y_pos, f"{town}")
        y_pos -= 0.15*inch
        c.drawString(4.5*inch, y_pos, f"SSN: XXX-XX-{random.randint(1000, 9999)}")
        
        # Calculate tax amounts (simplified calculations)
        wages = float(salary)
        federal_tax = wages * 0.22  # 22% federal tax (simplified)
        social_security = min(wages * 0.062, 10_453.20)  # 6.2% up to wage base
        medicare = wages * 0.0145  # 1.45% medicare
        state_tax = wages * 0.05  # 5% state tax (simplified)
        
        # Wage and Tax Information
        y_pos = height - 4*inch
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.HexColor("#5B8C85"))
        c.drawString(1*inch, y_pos, "Wages and Taxes:")
        c.setFillColor(colors.black)
        
        y_pos -= 0.4*inch
        c.setFont("Helvetica", 9)
        
        # Box 1 - Wages
        c.drawString(1*inch, y_pos, "1. Wages, tips, other compensation")
        c.drawString(5*inch, y_pos, f"${wages:,.2f}")
        
        y_pos -= 0.3*inch
        c.drawString(1*inch, y_pos, "2. Federal income tax withheld")
        c.drawString(5*inch, y_pos, f"${federal_tax:,.2f}")
        
        y_pos -= 0.3*inch
        c.drawString(1*inch, y_pos, "3. Social security wages")
        c.drawString(5*inch, y_pos, f"${wages:,.2f}")
        
        y_pos -= 0.3*inch
        c.drawString(1*inch, y_pos, "4. Social security tax withheld")
        c.drawString(5*inch, y_pos, f"${social_security:,.2f}")
        
        y_pos -= 0.3*inch
        c.drawString(1*inch, y_pos, "5. Medicare wages and tips")
        c.drawString(5*inch, y_pos, f"${wages:,.2f}")
        
        y_pos -= 0.3*inch
        c.drawString(1*inch, y_pos, "6. Medicare tax withheld")
        c.drawString(5*inch, y_pos, f"${medicare:,.2f}")
        
        y_pos -= 0.5*inch
        c.drawString(1*inch, y_pos, "17. State income tax")
        c.drawString(5*inch, y_pos, f"${state_tax:,.2f}")
        
        y_pos -= 0.3*inch
        c.drawString(1*inch, y_pos, "19. Local income tax")
        c.drawString(5*inch, y_pos, "$0.00")
        
        # Footer
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(colors.HexColor("#7D7D7D"))
        c.drawString(1*inch, 1*inch, "This is a generated document for demonstration purposes.")
        c.drawString(1*inch, 0.8*inch, f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        
        # Watermark
        c.setFont("Helvetica-Bold", 60)
        c.setFillColor(colors.HexColor("#E8DED2"))
        c.saveState()
        c.translate(4.25*inch, 5*inch)
        c.rotate(45)
        c.drawCentredString(0, 0, "SAMPLE")
        c.restoreState()
        
        c.save()
        print(f"✓ Generated W-2 for {first_name}: {filepath}")
        return filepath
    
    def get_w2_path(self, first_name: str, year: int = 2024) -> Optional[str]:
        """
        Get the path to an existing W-2 or None if it doesn't exist
        
        Args:
            first_name: Employee's first name
            year: Tax year
            
        Returns:
            Path to W-2 PDF if it exists, None otherwise
        """
        filename = f"{first_name}_W2_{year}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        if os.path.exists(filepath):
            return filepath
        return None
    
    def list_all_w2s(self) -> List[str]:
        """
        List all W-2 files in the output directory
        
        Returns:
            List of W-2 filenames
        """
        if not os.path.exists(self.output_dir):
            return []
        
        return [f for f in os.listdir(self.output_dir) if f.endswith('.pdf')]


if __name__ == "__main__":
    # Test the generator
    test_employee = {
        'First Name': 'Thomas',
        'Employee ID': 'EID2480002',
        'Salary': 61933,
        'Town': 'Harrowgate'
    }
    
    generator = W2Generator()
    w2_path = generator.generate_w2(test_employee, 2024)
    print(f"Test W-2 generated at: {w2_path}")
