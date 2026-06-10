from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Update the questioncategory enum type
enums = [
    'relationship_boundaries',
    'intimacy',
    'money_career',
    'dating_goals',
    'religion',
    'politics',
    'communication'
]

for enum_value in enums:
    try:
        db.execute(text(f"ALTER TYPE questioncategory ADD VALUE '{enum_value}'"))
        db.commit()
        print(f'✓ Added {enum_value}')
    except Exception as e:
        print(f'⚠ {enum_value}: {str(e)}')
        db.rollback()

db.close()
print('✓ Enum update complete')
