#!/usr/bin/env python3
"""
PocketSmart AI Server Runner
"""
import uvicorn

if __name__ == "__main__":
    print("==========================================================")
    print(">> Starting PocketSmart AI Server at http://127.0.0.1:8000")
    print(">> Demo Account: demo@pocketsmart.ai | password123")
    print("==========================================================")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
