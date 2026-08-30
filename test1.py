#!/usr/bin/env python3
"""
Admin Account Management Script
Use this to list, reset password, or delete admin accounts
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice-assistant/backend'))

from app.db.database import SessionLocal
from app.models.admin import AdminUser

def list_admins():
    """List all admin users"""
    db = SessionLocal()
    try:
        admins = db.query(AdminUser).all()
        
        if not admins:
            print("❌ No admin users found in the database.")
            return
        
        print("\n" + "=" * 60)
        print("EXISTING ADMIN USERS")
        print("=" * 60)
        for admin in admins:
            print(f"\n  ID: {admin.id}")
            print(f"  Username: {admin.username}")
            print(f"  Email: {admin.email}")
            print(f"  Is Active: {admin.is_active}")
            print(f"  Created: {admin.created_at}")
            print("-" * 60)
    finally:
        db.close()

def reset_password(username: str, new_password: str):
    """Reset password for an admin user"""
    db = SessionLocal()
    try:
        admin = db.query(AdminUser).filter(AdminUser.username == username).first()
        
        if not admin:
            print(f"❌ Admin not found: {username}")
            return False
        
        admin.set_password(new_password)
        db.commit()
        print(f"✅ Password reset successfully for admin: {admin.username}")
        print(f"   Email: {admin.email}")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error resetting password: {e}")
        return False
    finally:
        db.close()

def delete_all_admins():
    """Delete all admin users (use with caution!)"""
    db = SessionLocal()
    try:
        count = db.query(AdminUser).count()
        
        if count == 0:
            print("❌ No admin users to delete.")
            return False
        
        confirm = input(f"\n⚠️  WARNING: This will delete ALL {count} admin user(s). Are you sure? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("❌ Operation cancelled.")
            return False
        
        db.query(AdminUser).delete()
        db.commit()
        print(f"✅ Deleted {count} admin user(s). You can now create a new admin via signup.")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error deleting admins: {e}")
        return False
    finally:
        db.close()

def main():
    print("\n" + "=" * 60)
    print("ADMIN ACCOUNT MANAGEMENT")
    print("=" * 60)
    print("\nOptions:")
    print("1. List all admin users")
    print("2. Reset admin password")
    print("3. Delete all admin users (allows new signup)")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        list_admins()
    elif choice == "2":
        username = input("\nEnter admin username: ").strip()
        if not username:
            print("❌ Username is required!")
            return
        new_password = input("Enter new password: ").strip()
        if not new_password:
            print("❌ Password is required!")
            return
        if len(new_password) < 8:
            print("⚠️  Warning: Password is less than 8 characters")
            confirm = input("Continue anyway? (yes/no): ")
            if confirm.lower() != 'yes':
                return
        reset_password(username, new_password)
    elif choice == "3":
        delete_all_admins()
    elif choice == "4":
        print("Goodbye!")
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()