from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("Recreating questioncategory enum...")

# First, temporarily change the column to text
try:
    db.execute(text("ALTER TABLE compatibility_questions ALTER COLUMN category TYPE TEXT"))
    db.commit()
    print("✓ Changed category column to TEXT")
except Exception as e:
    print(f"Error changing column: {e}")
    db.rollback()

# Drop the old enum
try:
    db.execute(text("DROP TYPE IF EXISTS questioncategory CASCADE"))
    db.commit()
    print("✓ Dropped old questioncategory enum")
except Exception as e:
    print(f"Error dropping enum: {e}")
    db.rollback()

# Create the new enum with lowercase values
try:
    db.execute(text(
        "CREATE TYPE questioncategory AS ENUM ("
        "'relationship_boundaries', 'intimacy', 'lifestyle', 'money_career', "
        "'family', 'dating_goals', 'religion', 'politics', 'communication'"
        ")"
    ))
    db.commit()
    print("✓ Created new questioncategory enum")
except Exception as e:
    print(f"Error creating enum: {e}")
    db.rollback()

# Change the column back to enum
try:
    db.execute(text("ALTER TABLE compatibility_questions ALTER COLUMN category TYPE questioncategory USING category::questioncategory"))
    db.commit()
    print("✓ Changed category column back to questioncategory enum")
except Exception as e:
    print(f"Error changing column back: {e}")
    db.rollback()

# Do the same for questiontype
print("\nRecreating questiontype enum...")

try:
    db.execute(text("ALTER TABLE compatibility_questions ALTER COLUMN question_type TYPE TEXT"))
    db.commit()
    print("✓ Changed question_type column to TEXT")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()

try:
    db.execute(text("DROP TYPE IF EXISTS questiontype CASCADE"))
    db.commit()
    print("✓ Dropped old questiontype enum")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()

try:
    db.execute(text("CREATE TYPE questiontype AS ENUM ('multiple_choice', 'scale', 'yes_no', 'text')"))
    db.commit()
    print("✓ Created new questiontype enum")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()

try:
    db.execute(text("ALTER TABLE compatibility_questions ALTER COLUMN question_type TYPE questiontype USING question_type::questiontype"))
    db.commit()
    print("✓ Changed question_type column back to questiontype enum")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()

db.close()
print("\n✓ Enum recreation complete!")
