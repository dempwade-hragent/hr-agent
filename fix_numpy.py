"""
NumPy Compatibility Fix Script
Run this to fix the NumPy 2.x compatibility error
"""

import subprocess
import sys

print("="*60)
print("  NUMPY COMPATIBILITY FIX")
print("="*60)
print()
print("This will downgrade NumPy to a compatible version (1.x)")
print()

# Uninstall current NumPy
print("Step 1: Uninstalling NumPy 2.x...")
try:
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "numpy", "-y"])
    print("✓ NumPy uninstalled")
except Exception as e:
    print(f"Note: {e}")

print()

# Install compatible NumPy version
print("Step 2: Installing NumPy 1.x (compatible version)...")
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy<2.0.0"])
    print("✓ NumPy 1.x installed")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

print()

# Reinstall pandas to ensure compatibility
print("Step 3: Reinstalling pandas...")
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--force-reinstall", "pandas"])
    print("✓ Pandas reinstalled")
except Exception as e:
    print(f"Note: {e}")

print()
print("="*60)
print("  FIX COMPLETE!")
print("="*60)
print()
print("You can now run: python backend.py")
print()
