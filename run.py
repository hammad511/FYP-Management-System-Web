"""
Entry point to run the FYP Management System.
This file sits at the project root and imports the Flask app from backend/.
"""
import sys
import os

# Add backend directory to Python path

from backend.app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
