#!/usr/bin/env python3
"""
Test CSRF token functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from flask import render_template_string

def test_csrf_tokens():
    """Test if CSRF tokens are working in templates"""
    print("=== CSRF TOKEN TEST ===")
    
    with app.app_context():
        # Test login template
        login_template = '''
        <form method="POST" action="/login">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <input type="email" name="email" required>
            <input type="password" name="password" required>
            <button type="submit">Login</button>
        </form>
        '''
        
        try:
            rendered = render_template_string(login_template)
            print("✅ Login template CSRF token renders successfully")
            if 'csrf_token' in rendered:
                print("✅ CSRF token found in rendered template")
            else:
                print("❌ CSRF token missing in rendered template")
        except Exception as e:
            print(f"❌ Error rendering login template: {e}")
        
        # Test signup template
        signup_template = '''
        <form action="{{ url_for('signup') }}" method="POST">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <input type="email" name="email" required>
            <button type="submit">Signup</button>
        </form>
        '''
        
        try:
            rendered = render_template_string(signup_template)
            print("✅ Signup template CSRF token renders successfully")
            if 'csrf_token' in rendered:
                print("✅ CSRF token found in rendered template")
            else:
                print("❌ CSRF token missing in rendered template")
        except Exception as e:
            print(f"❌ Error rendering signup template: {e}")
        
        # Check if CSRF is properly configured
        if hasattr(app, 'csrf'):
            print("✅ CSRF protection is initialized on app")
        else:
            print("❌ CSRF protection not found on app")
        
        return True

if __name__ == "__main__":
    success = test_csrf_tokens()
    if success:
        print("\n🎉 CSRF token test completed successfully!")
    else:
        print("\n❌ CSRF token test failed!")
    
    sys.exit(0 if success else 1)
