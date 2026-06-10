#!/usr/bin/env python3
"""Test the questions endpoint directly"""
from app.db.session import SessionLocal
from app.services.compatibility_service import CompatibilityService
import json

db = SessionLocal()

print("Testing CompatibilityService.get_all_questions()...")
questions = CompatibilityService.get_all_questions(db)
print(f"Found {len(questions)} questions")

if questions:
    q = questions[0]
    print(f"\nFirst question:")
    print(f"  ID: {q.id}")
    print(f"  Text: {q.question_text}")
    print(f"  Category: {q.category}")
    print(f"  Type: {q.question_type}")
    print(f"  Options: {q.options}")
    
    # Try to serialize to dict (simulating API response)
    try:
        result = {
            "id": q.id,
            "question_text": q.question_text,
            "category": q.category,
            "question_type": q.question_type,
            "options": json.loads(q.options) if q.options else None,
            "scale_min": q.scale_min,
            "scale_max": q.scale_max,
            "scale_min_label": q.scale_min_label,
            "scale_max_label": q.scale_max_label,
            "weight": q.weight,
            "is_dealbreaker": q.is_dealbreaker,
            "order_index": q.order_index
        }
        print(f"\n✅ Successfully serialized question")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"\n❌ Error serializing: {e}")
else:
    print("❌ No questions found!")

db.close()
