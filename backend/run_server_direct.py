#!/usr/bin/env python3

import uvicorn
from main import app

if __name__ == "__main__":
    print("Starting AI-Lab backend server with full agent pipeline...")
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8001,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc() 