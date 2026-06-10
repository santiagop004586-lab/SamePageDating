#!/usr/bin/env python3
"""Test answer submission with boolean values"""
from app.db.session import SessionLocal
from app.services.compatibility_service import CompatibilityService
from app.services.profile_service import ProfileService
from app.schemas.compatibility import AnswerSubmit
from app.models.user import User

db = SessionLocal()

# Get first user
user = db.query(User).first()
if not user:
    print("❌ No users found! Create a user first.")
    db.close()
    exit(1)

print(f"Found user: {user.email}")

# Get user's profile
profile = ProfileService.get_profile_by_user(db, user.id)
if not profile:
    print("❌ No profile found! Create a profile first.")
    db.close()
    exit(1)

print(f"Found profile: {profile.id}")

# Try to submit a yes/no answer (question 11)
print("\nTesting boolean answer submission...")
answer_data = AnswerSubmit(
    question_id=11,
    boolean_answer=True,  # User's answer
    preferred_boolean_answer=False,  # Preferred partner answer
    importance=3,  # Very Important
    exclude_non_matching=False
)

try:
    result = CompatibilityService.submit_answer(db, profile.id, answer_data)
    print(f"✅ Answer submitted successfully!")
    print(f"   Answer ID: {result.id}")
    print(f"   Boolean answer (stored as int): {result.boolean_answer}")
    print(f"   Preferred boolean (stored as int): {result.preferred_boolean_answer}")
    print(f"   Importance: {result.importance}")
    print(f"   Exclude non-matching: {result.exclude_non_matching}")
except Exception as e:
    print(f"❌ Error submitting answer: {e}")
    import traceback
    traceback.print_exc()

db.close()
