import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.app import app, db, User
import datetime

with app.app_context():
    # Check if created_at column exists
    inspector = db.inspect(db.engine)
    columns = [c['name'] for c in inspector.get_columns('user')]
    
    if 'created_at' not in columns:
        print("Adding created_at column to User table...")
        with db.engine.begin() as conn:
            conn.execute('ALTER TABLE user ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP')
        print("✓ Column added successfully")
    else:
        print("✓ created_at column already exists")
    
    # Update any NULL created_at values to current timestamp
    users_with_null = User.query.filter(User.created_at == None).all()
    if users_with_null:
        print(f"Updating {len(users_with_null)} users with NULL created_at...")
        for user in users_with_null:
            user.created_at = datetime.datetime.now()
        db.session.commit()
        print("✓ Users updated")
    else:
        print("✓ No NULL created_at values found")
    
    print("\nDatabase migration complete!")
