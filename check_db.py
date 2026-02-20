from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    print('Database tables:')
    for table in inspector.get_table_names():
        print(f'  - {table}')
        
    # Check if admin user exists
    from app import User
    admin = User.query.filter_by(email='admin@example.com').first()
    if admin:
        print(f'\n✓ Admin user found: {admin.first_name} {admin.last_name}')
    else:
        print('\n✗ Admin user not found')
