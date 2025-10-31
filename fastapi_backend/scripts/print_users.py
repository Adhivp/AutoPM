"""Small helper script to print users from the configured database.

Usage:
  source ./autopm_venv/bin/activate
  python scripts/print_users.py

This prints each user's id, email and hashed_password so you can verify the seeded
account (adhivp04@gmail.com) and compare the hash to the expected SHA256 value.
"""
from database import SessionLocal, init_db
from models.user import User


def main():
    # Ensure tables exist
    init_db()

    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("No users found in database.")
            return

        print(f"Found {len(users)} user(s):\n")
        for u in users:
            print(f"id={u.id} email={u.email} is_active={u.is_active} hashed_password={u.hashed_password}")

    finally:
        db.close()


if __name__ == '__main__':
    main()
