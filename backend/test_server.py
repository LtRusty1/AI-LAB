#!/usr/bin/env python3

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing imports...")
    from main import app
    print("✓ FastAPI app imported successfully")
    
    print("Testing app initialization...")
    print(f"✓ App type: {type(app)}")
    print(f"✓ App title: {getattr(app, 'title', 'No title')}")
    
    print("All tests passed! The app should work.")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc() 