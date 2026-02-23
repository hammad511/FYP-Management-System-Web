"""
Script to force-create all database tables for the FYP Management System.
Run this if you get 'no such table' errors.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.app import app, db

with app.app_context():
    db.create_all()
    print('All tables created successfully.')
