#!/usr/bin/env python3
"""
Admin Account Management Script
Use this CLI utility to list, reset password, or delete admin accounts in the database.

Usage:
    python scripts/manage_admin.py list
    python scripts/manage_admin.py reset <username> <new_password>
    python scripts/manage_admin.py delete <username>
"""
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.db.database import SessionLocal
from app.models.admin import AdminUser


def list_admins():
    """List all admin users."""
    db = SessionLocal()
    try:
        admins = db.query(AdminUser).all()
        if not admins:
            print("[*] No admin users found in the database.")
            return
        
        print("\n" + "=" * 60)
        print("  EXISTING ADMIN USERS")
        print("=" * 60)
        for admin in admins:
            print(f"  ID: {admin.id}")
            print(f"  Username: {admin.username}")
            print(f"  Email: {admin.email}")
            print(f"  Is Active: {admin.is_active}")
            print(f"  Created: {admin.created_at}")
            print("-" * 60)
    finally:
        db.close()


def reset_password(username: str, new_password: str) -> bool:
    """Reset password for an existing admin user."""
    db = SessionLocal()
    try:
        admin = db.query(AdminUser).filter(AdminUser.username == username).first()
        if not admin:
            print(f"[-] Admin user not found: {username}")
            return False
        
        admin.set_password(new_password)
        db.commit()
        print(f"[+] Password reset successfully for admin: {admin.username}")
        print(f"    Email: {admin.email}")
        return True
    except Exception as e:
        db.rollback()
        print(f"[-] Error resetting password: {e}")
        return False
    finally:
        db.close()


def delete_admin(username: str) -> bool:
    """Delete an admin user account."""
    db = SessionLocal()
    try:
        admin = db.query(AdminUser).filter(AdminUser.username == username).first()
        if not admin:
            print(f"[-] Admin user not found: {username}")
            return False
        
        db.delete(admin)
        db.commit()
        print(f"[+] Deleted admin account: {username}")
        return True
    except Exception as e:
        db.rollback()
        print(f"[-] Error deleting admin: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/manage_admin.py list")
        print("  python scripts/manage_admin.py reset <username> <new_password>")
        print("  python scripts/manage_admin.py delete <username>")
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    if cmd == "list":
        list_admins()
    elif cmd == "reset" and len(sys.argv) >= 4:
        reset_password(sys.argv[2], sys.argv[3])
    elif cmd == "delete" and len(sys.argv) >= 3:
        delete_admin(sys.argv[2])
    else:
        print(f"[-] Unknown command or missing arguments: {cmd}")
