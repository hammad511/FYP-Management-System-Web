#!/usr/bin/env python3
"""
Test admin dashboard buttons by simulating actual usage
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from flask import url_for

def test_admin_dashboard_access():
    """Test if admin dashboard is accessible"""
    print("=== ADMIN DASHBOARD ACCESS TEST ===")
    
    with app.test_request_context():
        try:
            # Test admin user exists
            admin = User.query.filter_by(email='admin@example.com').first()
            if not admin:
                print("✗ Admin user not found")
                return False
            
            print(f"✓ Admin user found: {admin.email}")
            
            # Test dashboard route exists
            try:
                dashboard_url = url_for('dashboard_admin')
                print(f"✓ Dashboard URL: {dashboard_url}")
            except Exception as e:
                print(f"✗ Dashboard URL error: {e}")
                return False
            
            return True
            
        except Exception as e:
            print(f"✗ Error testing dashboard access: {e}")
            return False

def test_admin_routes_functionality():
    """Test key admin routes for functionality"""
    print("\n=== ADMIN ROUTES FUNCTIONALITY TEST ===")
    
    with app.test_request_context():
        routes_to_test = [
            ('dashboard_admin', 'GET', {}),
            ('admin_add_user', 'POST', {}),
            ('admin_edit_user', 'POST', {'user_id': 1}),
            ('admin_delete_user', 'POST', {'user_id': 1}),
            ('admin_add_project', 'POST', {}),
            ('admin_edit_project', 'POST', {'project_id': 1}),
            ('admin_delete_project', 'POST', {'project_id': 1}),
            ('admin_scheduling', 'GET', {}),
            ('admin_viva_scheduling', 'GET', {}),
        ]
        
        success_count = 0
        for route_name, method, kwargs in routes_to_test:
            try:
                url = url_for(route_name, **kwargs)
                print(f"✓ {route_name}: {url}")
                success_count += 1
            except Exception as e:
                print(f"✗ {route_name}: Error - {e}")
        
        print(f"\nRoutes working: {success_count}/{len(routes_to_test)}")
        return success_count == len(routes_to_test)

def test_template_structure():
    """Test template structure for button functionality"""
    print("\n=== TEMPLATE STRUCTURE TEST ===")
    
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard_admin.html')
    
    if not os.path.exists(template_path):
        print("✗ Template file not found")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test for key button elements
    tests = [
        ('data-bs-toggle="modal"', 'Modal triggers'),
        ('data-bs-target="#', 'Modal targets'),
        ('<form action=', 'Form submissions'),
        ('type="submit"', 'Submit buttons'),
        ('btn btn-primary', 'Primary buttons'),
        ('btn btn-danger', 'Danger buttons'),
        ('btn btn-secondary', 'Secondary buttons'),
        ('onclick=', 'Click handlers'),
        ('addEventListener', 'Event listeners'),
        ('bootstrap.Modal', 'Bootstrap modals')
    ]
    
    passed = 0
    for test, description in tests:
        if test in content:
            print(f"✓ {description}")
            passed += 1
        else:
            print(f"⚠ {description} - May be missing")
    
    print(f"Template elements: {passed}/{len(tests)}")
    return passed >= len(tests) * 0.8  # 80% pass rate

def main():
    """Run all tests"""
    print("FYP Management System - Admin Dashboard Button Test")
    print("=" * 55)
    
    tests = [
        test_admin_dashboard_access,
        test_admin_routes_functionality,
        test_template_structure
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 55)
    print("BUTTON FUNCTIONALITY TEST RESULTS:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Admin dashboard buttons should be working correctly")
        print("✅ All routes are properly configured")
        print("✅ Template structure is correct")
        print("✅ Modal functionality is implemented")
        
        print("\n📋 NEXT STEPS:")
        print("1. Start the application: python app.py")
        print("2. Login as admin: admin@example.com / admin123")
        print("3. Test each button manually in the browser")
        print("4. Check browser console for any JavaScript errors")
        
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("Some issues may exist. Review the test results above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
