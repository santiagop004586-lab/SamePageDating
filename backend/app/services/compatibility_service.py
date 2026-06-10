from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.compatibility_question import CompatibilityQuestion, QuestionCategory
from app.models.compatibility_answer import CompatibilityAnswer
from app.models.profile import Profile
from app.schemas.compatibility import AnswerSubmit
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class CompatibilityService:
    """Service for compatibility questionnaire and scoring"""

    @staticmethod
    def get_all_questions(db: Session, category: str = None) -> List[CompatibilityQuestion]:
        """Get all active questions, optionally filtered by category"""
        query = db.query(CompatibilityQuestion).filter(CompatibilityQuestion.is_active == True)
        
        if category:
            query = query.filter(CompatibilityQuestion.category == category)
        
        return query.order_by(CompatibilityQuestion.order_index).all()

    @staticmethod
    def submit_answer(db: Session, profile_id: int, answer_data: AnswerSubmit) -> CompatibilityAnswer:
        """Submit or update an answer to a question"""
        # Check if answer already exists
        existing = db.query(CompatibilityAnswer).filter(
            and_(
                CompatibilityAnswer.profile_id == profile_id,
                CompatibilityAnswer.question_id == answer_data.question_id
            )
        ).first()
        
        # Convert boolean answers to integers (database expects 0 or 1)
        data_dict = answer_data.model_dump()
        if data_dict.get('boolean_answer') is not None:
            data_dict['boolean_answer'] = 1 if data_dict['boolean_answer'] else 0
        if data_dict.get('preferred_boolean_answer') is not None:
            data_dict['preferred_boolean_answer'] = 1 if data_dict['preferred_boolean_answer'] else 0
        
        if existing:
            # Update existing answer
            update_dict = {k: v for k, v in data_dict.items() if k != 'question_id'}
            for field, value in update_dict.items():
                if value is not None:
                    setattr(existing, field, value)
            
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new answer
            answer = CompatibilityAnswer(
                profile_id=profile_id,
                **data_dict
            )
            db.add(answer)
            db.commit()
            db.refresh(answer)
            logger.info(f"Answer submitted for profile {profile_id}, question {answer_data.question_id}")
            return answer

    @staticmethod
    def get_profile_answers(db: Session, profile_id: int) -> List[CompatibilityAnswer]:
        """Get all answers for a profile"""
        return db.query(CompatibilityAnswer).filter(
            CompatibilityAnswer.profile_id == profile_id
        ).all()

    @staticmethod
    def get_questionnaire_progress(db: Session, profile_id: int) -> Dict:
        """Get questionnaire completion progress"""
        total_questions = db.query(CompatibilityQuestion).filter(
            CompatibilityQuestion.is_active == True
        ).count()
        
        answered_questions = db.query(CompatibilityAnswer).filter(
            CompatibilityAnswer.profile_id == profile_id
        ).count()
        
        completion_percentage = int((answered_questions / total_questions * 100)) if total_questions > 0 else 0
        
        return {
            "total_questions": total_questions,
            "answered_questions": answered_questions,
            "completion_percentage": completion_percentage,
            "is_complete": answered_questions >= total_questions
        }

    @staticmethod
    def calculate_compatibility(db: Session, profile1_id: int, profile2_id: int) -> Dict:
        """
        Calculate compatibility score between two profiles
        Returns overall score (0-100) and category breakdown
        """
        # Get all answers for both profiles
        answers1 = {a.question_id: a for a in CompatibilityService.get_profile_answers(db, profile1_id)}
        answers2 = {a.question_id: a for a in CompatibilityService.get_profile_answers(db, profile2_id)}
        
        # Get all questions
        questions = {q.id: q for q in CompatibilityService.get_all_questions(db)}
        
        # Find common questions both answered
        common_question_ids = set(answers1.keys()) & set(answers2.keys())
        
        if not common_question_ids:
            return {
                "overall_score": 0,
                "category_scores": {},
                "dealbreaker_count": 0,
                "compatible": False
            }
        
        total_score = 0
        total_weight = 0
        category_scores = {}
        dealbreaker_count = 0
        
        for question_id in common_question_ids:
            question = questions[question_id]
            answer1 = answers1[question_id]
            answer2 = answers2[question_id]
            
            # Calculate similarity for this question (0-100)
            similarity = CompatibilityService._calculate_answer_similarity(question, answer1, answer2)
            
            # Weight by question importance and user importance
            weight = question.weight * ((answer1.importance + answer2.importance) / 2)
            
            # Track category scores
            category = question.category.value
            if category not in category_scores:
                category_scores[category] = {"score": 0, "weight": 0}
            
            category_scores[category]["score"] += similarity * weight
            category_scores[category]["weight"] += weight
            
            total_score += similarity * weight
            total_weight += weight
            
            # Check dealbreakers
            if question.is_dealbreaker and similarity < 50:
                dealbreaker_count += 1
        
        # Calculate overall score
        overall_score = int(total_score / total_weight) if total_weight > 0 else 0
        
        # Calculate category averages
        for category in category_scores:
            cat_weight = category_scores[category]["weight"]
            if cat_weight > 0:
                category_scores[category] = int(category_scores[category]["score"] / cat_weight)
            else:
                category_scores[category] = 0
        
        # Determine compatibility (must pass dealbreakers and have decent overall score)
        compatible = dealbreaker_count == 0 and overall_score >= 60
        
        return {
            "overall_score": overall_score,
            "category_scores": category_scores,
            "dealbreaker_count": dealbreaker_count,
            "compatible": compatible
        }

    @staticmethod
    def _calculate_answer_similarity(
        question: CompatibilityQuestion,
        answer1: CompatibilityAnswer,
        answer2: CompatibilityAnswer
    ) -> float:
        """Calculate similarity between two answers (0-100)"""
        
        if question.question_type.value == "yes_no":
            # Binary match
            return 100.0 if answer1.boolean_answer == answer2.boolean_answer else 0.0
        
        elif question.question_type.value == "multiple_choice":
            # Exact match for choices
            return 100.0 if answer1.choice_answer == answer2.choice_answer else 0.0
        
        elif question.question_type.value == "scale":
            # Scale difference (closer = more compatible)
            if answer1.numeric_answer is None or answer2.numeric_answer is None:
                return 50.0
            
            scale_range = question.scale_max - question.scale_min
            if scale_range == 0:
                return 100.0
            
            difference = abs(answer1.numeric_answer - answer2.numeric_answer)
            similarity = max(0, 100 - (difference / scale_range * 100))
            return similarity
        
        elif question.question_type.value == "text":
            # Text comparison is complex, for now return neutral score
            # Could implement NLP similarity in the future
            return 50.0
        
        return 50.0
