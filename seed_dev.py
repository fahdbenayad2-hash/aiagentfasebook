import hashlib
import secrets
from app.database import SessionLocal
from app.models import User


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{h}"


def seed():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@maria.dz").first()
        if existing:
            print(f"User already exists: {existing.email}")
            return

        user = User(
            name="المطور",
            email="admin@maria.dz",
            phone="0550000000",
            password_hash=hash_password("admin123"),
            credits=999999,
            is_developer=True,
        )
        db.add(user)
        db.commit()
        print(f"Dev account created: {user.email} / admin123")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
