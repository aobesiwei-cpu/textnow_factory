#!/usr/bin/env python3
"""
Database initialization script
Usage:
    python database/init_db.py          # Initialize tables and create default admin
    python database/init_db.py --clean  # Clear database (use with caution!)
"""

import sys
import os
from pathlib import Path

# Add project root directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_utils import engine, Base
from database.db_models import TbAccount, TbReplyRule, TbAdminUser
from utils.encrypt_util import hash_pwd
from config.db_config import DB_URI

def init_tables():
    """Initialize all database tables"""
    try:
        print("[INFO] Connecting to database...")
        print(f"[INFO] Database URI: {DB_URI}")
        
        print("[INFO] Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("[✓] Database tables initialized successfully")
        return True
    except Exception as e:
        print(f"[✗] Database table initialization failed: {e}")
        return False

def create_super_admin():
    """Create default super admin account"""
    try:
        from config.db_config import SessionLocal
        db = SessionLocal()
        
        # Check if admin user already exists
        exist = db.query(TbAdminUser).filter_by(username="admin").first()
        if exist:
            print("[!] Default admin account already exists, skipping creation")
            db.close()
            return True
        
        # Create default admin user
        admin = TbAdminUser(
            username="admin",
            password_hash=hash_pwd("admin123"),
            is_super=1
        )
        db.add(admin)
        db.commit()
        print("[✓] Default admin account created successfully")
        print("    Username: admin")
        print("    Password: admin123")
        print("    [WARNING] MUST change password before going live!")
        db.close()
        return True
    except Exception as e:
        print(f"[✗] Failed to create admin account: {e}")
        return False

def clean_database():
    """Clear all database tables (use with caution!)"""
    try:
        print("[WARNING] About to delete all database tables...")
        confirm = input("Confirm delete all database tables? (yes/no): ")
        if confirm.lower() != 'yes':
            print("[CANCEL] Operation cancelled")
            return False
        
        print("[INFO] Deleting all database tables...")
        Base.metadata.drop_all(bind=engine)
        print("[✓] All database tables deleted")
        return True
    except Exception as e:
        print(f"[✗] Failed to delete database tables: {e}")
        return False

def main():
    """Main function"""
    print("="*60)
    print("textnow_factory Database Initialization Tool")
    print("="*60)
    
    # Check if clean database flag is provided
    if "--clean" in sys.argv:
        if not clean_database():
            sys.exit(1)
    
    # Initialize database tables
    if not init_tables():
        sys.exit(1)
    
    # Create default admin user
    if not create_super_admin():
        sys.exit(1)
    
    print("="*60)
    print("[✓] Database initialization completed!")
    print("="*60)

if __name__ == "__main__":
    main()
