from app.db.session import SessionLocal
from app.models.compatibility_question import CompatibilityQuestion

db = SessionLocal()
questions = db.query(CompatibilityQuestion).all()
print(f'\nTotal questions: {len(questions)}\n')

for q in questions:
    print(f'{q.id}. [{q.category}] {q.question_text[:70]}...')

db.close()
