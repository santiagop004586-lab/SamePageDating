from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password

db = SessionLocal()
admin = db.query(User).filter(User.email == "santiagop004586@gmail.com").first()

if admin:
    admin.is_admin = True
    admin.is_verified = True
    db.commit()
    print("✅ Updated existing user to admin")
else:
    admin = User(
        email="santiagop004586@gmail.com",
        hashed_password=hash_password("admin123"),
        is_admin=True,
        is_verified=True,
        full_name="Admin User"
    )
    db.add(admin)
    db.commit()
    print("✅ Created new admin user")

print("Email: santiagop004586@gmail.com")
print("Password: admin123")
print(f"Admin: {admin.is_admin}")

db.close()
