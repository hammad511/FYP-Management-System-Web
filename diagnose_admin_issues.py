#!/usr/bin/env python3
"""
Diagnose specific issues with admin dashboard buttons
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
import re

def check_template_form_actions():
    """Check all form actions in dashboard_admin.html"""
    print("=== TEMPLATE FORM ACTIONS CHECK ===")
    
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard_admin.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all form actions
    form_actions = re.findall(r'action="([^"]*)"', content)
    print("Found form actions:")
    for action in form_actions:
        print(f"  - {action}")
    
    # Find all url_for calls
    url_for_calls = re.findall(r'url_for\([\'"]([^\'"]*)[\'"]', content)
    print("\nFound url_for calls:")
    for call in url_for_calls:
        print(f"  - {call}")
    
    return form_actions, url_for_calls

def check_route_existence():
    """Check if all required routes exist"""
    print("\n=== ROUTE EXISTENCE CHECK ===")
    
    with app.app_context():
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard_admin.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract route names from url_for calls
        url_for_calls = re.findall(r'url_for\([\'"]([^\'"]*)[\'"]', content)
        
        missing_routes = []
        existing_routes = []
        
        for route_name in url_for_calls:
            try:
                # Try to find the route
                found = False
                for rule in app.url_map.iter_rules():
                    if rule.endpoint == route_name:
                        found = True
                        existing_routes.append(route_name)
                        break
                
                if not found:
                    missing_routes.append(route_name)
                    
            except Exception as e:
                missing_routes.append(f"{route_name} (Error: {e})")
        
        print(f"✓ Found {len(existing_routes)} existing routes:")
        for route in sorted(set(existing_routes)):
            print(f"  - {route}")
        
        if missing_routes:
            print(f"\n✗ Missing {len(missing_routes)} routes:")
            for route in sorted(set(missing_routes)):
                print(f"  - {route}")
        else:
            print("\n✓ All routes found!")
        
        return len(missing_routes) == 0

def check_modal_buttons():
    """Check modal button implementations"""
    print("\n=== MODAL BUTTONS CHECK ===")
    
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard_admin.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all modals
    modals = re.findall(r'id="([^"]*)"[^>]*class="[^"]*modal', content)
    print("Found modals:")
    for modal in modals:
        print(f"  - {modal}")
    
    # Find all modal triggers
    modal_triggers = re.findall(r'data-bs-toggle="modal"[^>]*data-target="([^"]*)"', content)
    modal_triggers.extend(re.findall(r'data-bs-toggle="modal"[^>]*data-bs-target="([^"]*)"', content))
    
    print("\nFound modal triggers:")
    for trigger in modal_triggers:
        print(f"  - {trigger}")
    
    # Check for missing modals
    missing_modals = []
    for trigger in modal_triggers:
        modal_id = trigger.replace('#', '')
        if modal_id not in modals:
            missing_modals.append(trigger)
    
    if missing_modals:
        print(f"\n✗ Missing modals for triggers:")
        for modal in missing_modals:
            print(f"  - {modal}")
    else:
        print("\n✓ All modals found!")
    
    return len(missing_modals) == 0

def check_javascript_handlers():
    """Check JavaScript event handlers"""
    print("\n=== JAVASCRIPT HANDLERS CHECK ===")
    
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard_admin.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key JavaScript patterns
    js_patterns = [
        ('addEventListener', 'Event listeners'),
        ('onclick=', 'Inline onclick handlers'),
        ('fetch(', 'AJAX calls'),
        ('bootstrap.Modal', 'Bootstrap modals'),
        ('preventDefault', 'Form submission handling')
    ]
    
    for pattern, description in js_patterns:
        if pattern in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ⚠ {description} - May be missing")
    
    # Check for section navigation
    if 'section-link' in content:
        print("  ✓ Section navigation links")
    else:
        print("  ⚠ Section navigation links - May be missing")

def check_common_issues():
    """Check for common admin dashboard issues"""
    print("\n=== COMMON ISSUES CHECK ===")
    
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard_admin.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Check for missing form submissions
    if 'handleUserFormSubmit' not in content:
        issues.append("Missing form submission handler")
    
    # Check for missing CSRF tokens
    if 'csrf_token' not in content:
        issues.append("Missing CSRF tokens")
    
    # Check for missing error handling
    if 'try{' not in content or 'catch(' not in content:
        issues.append("Missing error handling in JavaScript")
    
    # Check for missing confirmation dialogs
    if 'confirm(' not in content:
        issues.append("Missing confirmation dialogs for destructive actions")
    
    if issues:
        print("Potential issues found:")
        for issue in issues:
            print(f"  ⚠ {issue}")
    else:
        print("✓ No common issues detected")
    
    return len(issues) == 0

def main():
    """Run all diagnostics"""
    print("FYP Management System - Admin Dashboard Issue Diagnosis")
    print("=" * 60)
    
    # Run all checks
    form_actions, url_for_calls = check_template_form_actions()
    routes_ok = check_route_existence()
    modals_ok = check_modal_buttons()
    check_javascript_handlers()
    common_ok = check_common_issues()
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS SUMMARY:")
    
    if routes_ok and modals_ok and common_ok:
        print("🎉 No major issues detected!")
        print("✓ All routes exist")
        print("✓ All modals are properly defined")
        print("✓ JavaScript handlers are present")
    else:
        print("⚠️ Issues found that need to be addressed:")
        if not routes_ok:
            print("✗ Some routes are missing")
        if not modals_ok:
            print("✗ Some modals are missing")
        if not common_ok:
            print("✗ Common implementation issues detected")
    
    print(f"\n📊 Statistics:")
    print(f"  - Form actions: {len(form_actions)}")
    print(f"  - URL routes: {len(url_for_calls)}")
    
    return routes_ok and modals_ok and common_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
