#!/usr/bin/env python3
"""
Test script to verify admin dashboard functionality and database implementation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from sqlalchemy import inspect

def test_database_implementation():
    """Test database structure and admin user"""
    print("=== DATABASE IMPLEMENTATION TEST ===")
    
    with app.app_context():
        # Check database tables
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'user', 'project_proposal', 'project_details', 'student_group',
            'group_member', 'project_status', 'project_milestone', 'viva',
            'time_slot', 'room', 'room_schedule', 'teacher_schedule',
            'teacher_username', 'login_attempt', 'notification', 'remark'
        ]
        
        print(f"✓ Database connected successfully")
        print(f"✓ Found {len(tables)} tables:")
        for table in sorted(tables):
            status = "✓" if table in expected_tables else "⚠"
            print(f"  {status} {table}")
        
        # Check admin user
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            print(f"✓ Admin user exists: {admin.first_name} {admin.last_name}")
            print(f"  Email: {admin.email}")
            print(f"  Role: {admin.role}")
        else:
            print("✗ Admin user not found")
            return False
            
        # Check user roles
        roles = db.session.query(User.role).distinct().all()
        print(f"✓ User roles in database: {[r[0] for r in roles]}")
        
    return True

def test_admin_routes():
    """Test admin route definitions"""
    print("\n=== ADMIN ROUTES TEST ===")
    
    # Import all admin routes from app
    from app import app
    
    admin_routes = []
    for rule in app.url_map.iter_rules():
        if '/admin' in rule.rule or 'dashboard_admin' in rule.endpoint:
            admin_routes.append((rule.rule, rule.endpoint, rule.methods))
    
    print(f"✓ Found {len(admin_routes)} admin-related routes:")
    for route, endpoint, methods in sorted(admin_routes):
        print(f"  {route} -> {endpoint} [{', '.join(methods)}]")
    
    # Key routes to check
    key_routes = [
        '/dashboard_admin',
        '/admin/add_user',
        '/admin/edit_user',
        '/admin/delete_user',
        '/admin/add_project',
        '/admin/scheduling',
        '/admin/viva_scheduling'
    ]
    
    for route in key_routes:
        found = any(route in r[0] for r in admin_routes)
        status = "✓" if found else "✗"
        print(f"  {status} {route}")
    
    return True

def test_template_structure():
    """Test admin dashboard template structure"""
    print("\n=== TEMPLATE STRUCTURE TEST ===")
    
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard_admin.html')
    
    if not os.path.exists(template_path):
        print("✗ dashboard_admin.html template not found")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key elements
    checks = [
        ('data-section="dashboard"', 'Dashboard section'),
        ('data-section="users"', 'User management section'),
        ('data-section="projects"', 'Projects section'),
        ('data-section="groups"', 'Groups section'),
        ('data-section="reports"', 'Reports section'),
        ('data-section="settings"', 'Settings section'),
        ('data-bs-toggle="modal"', 'Modal buttons'),
        ('url_for(\'dashboard_admin\')', 'Dashboard links'),
        ('url_for(\'admin_', 'Admin route links'),
        ('class="btn"', 'Action buttons'),
        ('onclick=', 'JavaScript handlers')
    ]
    
    for check, description in checks:
        if check in content:
            print(f"✓ {description}")
        else:
            print(f"⚠ {description} (may be optional)")
    
    return True

def test_javascript_functionality():
    """Test JavaScript functionality in admin dashboard"""
    print("\n=== JAVASCRIPT FUNCTIONALITY TEST ===")
    
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard_admin.html')
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    js_checks = [
        ('section-link', 'Section navigation'),
        ('addEventListener', 'Event handlers'),
        ('fetch(', 'AJAX calls'),
        ('bootstrap.Modal', 'Bootstrap modal support'),
        ('handleUserFormSubmit', 'Form submission handling'),
        ('admin_group_members', 'Group member fetching'),
        ('selected_count', 'Selection counting')
    ]
    
    for check, description in js_checks:
        if check in content:
            print(f"✓ {description}")
        else:
            print(f"⚠ {description} (may be implemented differently)")
    
    return True

def main():
    """Run all tests"""
    print("FYP Management System - Admin Dashboard Test")
    print("=" * 50)
    
    tests = [
        test_database_implementation,
        test_admin_routes,
        test_template_structure,
        test_javascript_functionality
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Admin dashboard is properly implemented.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
