import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.repositories.user_repository import UserRepository

def create_initial_users():
    """Create test users with different roles"""
    
    users = [
        {'username': 'operator1', 'password': 'password123', 'role': 'Operator'},
        {'username': 'supervisor1', 'password': 'password123', 'role': 'Supervisor'},
        {'username': 'manager1', 'password': 'password123', 'role': 'Management'},
    ]
    
    print("Creating initial users...\n")
    
    for user_data in users:
        try:
            # Check if user exists
            existing = UserRepository.get_user_by_username(user_data['username'])
            if existing:
                print(f"⚠️  User '{user_data['username']}' already exists")
                continue
            
            # Create user
            user = UserRepository.create_user(
                username=user_data['username'],
                password=user_data['password'],
                role=user_data['role']
            )
            print(f"✅ Created: {user['username']} (Role: {user['role']})")
            
        except Exception as e:
            print(f"❌ Error creating {user_data['username']}: {e}")
    
    print("\n" + "="*60)
    print("Test Credentials:")
    print("="*60)
    for user_data in users:
        print(f"Username: {user_data['username']}")
        print(f"Password: {user_data['password']}")
        print(f"Role: {user_data['role']}")
        print("-"*60)

if __name__ == '__main__':
    create_initial_users()
