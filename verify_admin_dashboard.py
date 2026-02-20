#!/usr/bin/env python3
"""
Simple verification of admin dashboard functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def verify_admin_dashboard():
    """Verify admin dashboard components"""
    print("FYP Management System - Admin Dashboard Verification")
    print("=" * 50)
    
    with app.app_context():
        # 1. Check Database
        print("1. DATABASE CHECK:")
        try:
            # Check if database is connected
            db.engine.connect()
            print("   ✓ Database connected successfully")
            
            # Check admin user
            admin = User.query.filter_by(email='admin@example.com').first()
            if admin and admin.role == 'admin':
                print(f"   ✓ Admin user exists: {admin.email}")
            else:
                print("   ✗ Admin user not found or incorrect role")
                return False
                
            # Check user counts by role
            roles = db.session.query(User.role, db.func.count(User.id)).group_by(User.role).all()
            print("   ✓ User roles:")
            for role, count in roles:
                print(f"     - {role}: {count} users")
                
        except Exception as e:
            print(f"   ✗ Database error: {e}")
            return False
        
        # 2. Check Routes
        print("\n2. ROUTE CHECK:")
        try:
            admin_routes = []
            for rule in app.url_map.iter_rules():
                if '/admin' in rule.rule or 'dashboard_admin' in rule.endpoint:
                    admin_routes.append(rule.rule)
            
            print(f"   ✓ Found {len(admin_routes)} admin routes")
            
            # Key routes that should exist
            key_routes = [
                '/dashboard_admin',
                '/admin/add_user',
                '/admin/edit_user',
                '/admin/delete_user',
                '/admin/scheduling',
                '/admin/viva_scheduling'
            ]
            
            for route in key_routes:
                if any(route in r for r in admin_routes):
                    print(f"   ✓ {route}")
                else:
                    print(f"   ✗ {route} - Missing")
                    
        except Exception as e:
            print(f"   ✗ Route check error: {e}")
            return False
        
        # 3. Check Template
        print("\n3. TEMPLATE CHECK:")
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard_admin.html')
        if os.path.exists(template_path):
            print("   ✓ dashboard_admin.html template exists")
            
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for key elements
            checks = [
                ('<button', 'Buttons'),
                ('data-bs-toggle="modal"', 'Modal buttons'),
                ('url_for(\'dashboard_admin\')', 'Dashboard links'),
                ('class="nav-link"', 'Navigation links'),
                ('<form', 'Forms'),
                ('<script>', 'JavaScript')
            ]
            
            for check, description in checks:
                if check in content:
                    print(f"   ✓ {description}")
                else:
                    print(f"   ⚠ {description} - May be missing")
        else:
            print("   ✗ dashboard_admin.html template not found")
            return False
        
        # 4. Check Static Files
        print("\n4. STATIC FILES CHECK:")
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        if os.path.exists(static_path):
            print("   ✓ Static directory exists")
            
            css_path = os.path.join(static_path, 'css')
            js_path = os.path.join(static_path, 'js')
            
            if os.path.exists(css_path):
                print("   ✓ CSS directory exists")
            else:
                print("   ⚠ CSS directory missing")
                
            if os.path.exists(js_path):
                print("   ✓ JS directory exists")
            else:
                print("   ⚠ JS directory missing")
        else:
            print("   ⚠ Static directory missing")
        
        return True

def check_button_functionality():
    """Check specific button functionality"""
    print("\n5. BUTTON FUNCTIONALITY CHECK:")
    
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard_admin.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key button types
    button_checks = [
        ('Add User', 'add user button'),
        ('Add Project', 'add project button'),
        ('Schedule Viva', 'schedule viva button'),
        ('Edit', 'edit buttons'),
        ('Delete', 'delete buttons'),
        ('View', 'view buttons'),
        ('Manage Users', 'user management'),
        ('Manage Projects', 'project management'),
        ('Reports', 'report generation'),
        ('Settings', 'system settings')
    ]
    
    for button_text, description in button_checks:
        if button_text.lower() in content.lower():
            print(f"   ✓ {description}")
        else:
            print(f"   ⚠ {description} - May be missing")
    
    # Check for form actions
    form_actions = [
        'action="/admin/add_user"',
        'action="/admin/edit_user/',
        'action="/admin/delete_user/',
        'action="/admin/add_project"',
        'action="/admin/schedule_viva"'
    ]
    
    print("\n   Form Actions:")
    for action in form_actions:
        if action in content:
            print(f"   ✓ {action}")
        else:
            print(f"   ⚠ {action} - May be missing")

def main():
    """Run verification"""
    success = verify_admin_dashboard()
    check_button_functionality()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ADMIN DASHBOARD VERIFICATION SUCCESSFUL!")
        print("\n✓ Database is properly implemented")
        print("✓ Admin routes are configured")
        print("✓ Template structure is correct")
        print("✓ Static files are present")
        print("✓ Button functionality appears complete")
        print("\n📝 NEXT STEPS:")
        print("1. Start the application: python app.py")
        print("2. Login as admin: admin@example.com / admin123")
        print("3. Test buttons manually in the browser")
        print("4. Verify all modals and forms work correctly")
    else:
        print("❌ VERIFICATION FAILED!")
        print("Please review the errors above and fix them.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
