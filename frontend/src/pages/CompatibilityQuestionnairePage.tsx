import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import compatibilityService, { CompatibilityQuestion, AnswerSubmit, CompatibilityAnswer } from '../services/compatibilityService';

const IMPORTANCE_LABELS = [
  'Not Important',
  'Somewhat Important',
  'Important',
  'Very Important',
  'Deal Breaker'
];

const CompatibilityQuestionnairePage: React.FC = () => {
  const [questions, setQuestions] = useState<CompatibilityQuestion[]>([]);
  const [existingAnswers, setExistingAnswers] = useState<Map<number, CompatibilityAnswer>>(new Map());
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showMessage, setShowMessage] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();
  const redirectMessage = (location.state as any)?.message;

  const [answer, setAnswer] = useState<{
    // My answer
    text?: string;
    choice?: string;
    numeric?: number;
    boolean?: boolean;
    // Preferred partner answer
    preferredText?: string;
    preferredChoice?: string;
    preferredNumeric?: number;
    preferredBoolean?: boolean;
    // Settings
    importance: number;
    excludeNonMatching: boolean;
  }>({
    importance: 0,
    excludeNonMatching: false,
  });

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    // Load saved answer when question changes
    const question = questions[currentIndex];
    if (question && existingAnswers.has(question.id)) {
      const existing = existingAnswers.get(question.id)!;
      setAnswer({
        text: existing.text_answer,
        choice: existing.choice_answer,
        numeric: existing.numeric_answer,
        boolean: existing.boolean_answer,
        preferredText: existing.preferred_text_answer,
        preferredChoice: existing.preferred_choice_answer,
        preferredNumeric: existing.preferred_numeric_answer,
        preferredBoolean: existing.preferred_boolean_answer,
        importance: existing.importance,
        excludeNonMatching: existing.exclude_non_matching,
      });
    } else {
      setAnswer({
        importance: 0,
        excludeNonMatching: false,
      });
    }
  }, [currentIndex, questions, existingAnswers]);

  const loadData = async () => {
    try {
      const [questionsData, answersData] = await Promise.all([
        compatibilityService.getQuestions(),
        compatibilityService.getMyAnswers().catch(() => [] as CompatibilityAnswer[])
      ]);
      
      setQuestions(questionsData);
      
      const answersMap = new Map<number, CompatibilityAnswer>();
      answersData.forEach(ans => answersMap.set(ans.question_id, ans));
      setExistingAnswers(answersMap);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    const question = questions[currentIndex];
    
    // Validate that user has provided their answer
    let hasUserAnswer = false;
    let hasPreferredAnswer = false;
    
    if (question.question_type === 'text') {
      hasUserAnswer = !!answer.text && answer.text.trim().length > 0;
      hasPreferredAnswer = !!answer.preferredText && answer.preferredText.trim().length > 0;
    } else if (question.question_type === 'multiple_choice') {
      hasUserAnswer = !!answer.choice;
      hasPreferredAnswer = !!answer.preferredChoice;
    } else if (question.question_type === 'scale') {
      hasUserAnswer = answer.numeric !== undefined;
      hasPreferredAnswer = answer.preferredNumeric !== undefined;
    } else if (question.question_type === 'yes_no') {
      hasUserAnswer = answer.boolean !== undefined;
      hasPreferredAnswer = answer.preferredBoolean !== undefined;
    }
    
    if (!hasUserAnswer) {
      alert('Please provide your answer before continuing.');
      return;
    }
    
    if (!hasPreferredAnswer) {
      alert('Please indicate your preferred partner answer before continuing.');
      return;
    }
    
    const answerData: AnswerSubmit = {
      question_id: question.id,
      importance: answer.importance,
      exclude_non_matching: answer.excludeNonMatching,
    };

    // My answer
    if (question.question_type === 'text') {
      answerData.text_answer = answer.text;
    } else if (question.question_type === 'multiple_choice') {
      answerData.choice_answer = answer.choice;
    } else if (question.question_type === 'scale') {
      answerData.numeric_answer = answer.numeric;
    } else if (question.question_type === 'yes_no') {
      answerData.boolean_answer = answer.boolean;
    }

    // Preferred partner answer
    if (question.question_type === 'text') {
      answerData.preferred_text_answer = answer.preferredText;
    } else if (question.question_type === 'multiple_choice') {
      answerData.preferred_choice_answer = answer.preferredChoice;
    } else if (question.question_type === 'scale') {
      answerData.preferred_numeric_answer = answer.preferredNumeric;
    } else if (question.question_type === 'yes_no') {
      answerData.preferred_boolean_answer = answer.preferredBoolean;
    }

    try {
      await compatibilityService.submitAnswer(answerData);
      
      // Move to next question or finish
      if (currentIndex < questions.length - 1) {
        setCurrentIndex(currentIndex + 1);
      } else {
        alert('Questionnaire completed! Redirecting to discovery...');
        navigate('/discovery');
      }
    } catch (error) {
      console.error('Error submitting answer:', error);
      alert('Error saving answer. Please try again.');
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  if (loading) return <div className="p-8">Loading questions...</div>;
  if (questions.length === 0) return <div className="p-8">No questions available.</div>;

  const question = questions[currentIndex];
  const progress = ((currentIndex + 1) / questions.length) * 100;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4">
        {/* Redirect Message Alert */}
        {redirectMessage && showMessage && (
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start justify-between">
              <div className="flex items-start">
                <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <p className="text-sm text-blue-800 font-medium">{redirectMessage}</p>
              </div>
              <button 
                onClick={() => setShowMessage(false)}
                className="text-blue-600 hover:text-blue-800"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        )}
        
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <div>
              <h1 className="text-2xl font-bold">Compatibility Questionnaire</h1>
              <p className="text-sm text-blue-600 font-medium mt-1">Required to access dating features</p>
            </div>
            <span className="text-sm text-gray-600">
              Question {currentIndex + 1} of {questions.length}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          {/* Question Header */}
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <span className="inline-block bg-blue-100 text-blue-800 text-xs px-3 py-1 rounded-full font-medium">
                {question.category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </span>
              {question.is_dealbreaker && (
                <span className="inline-block bg-red-100 text-red-800 text-xs px-3 py-1 rounded-full font-medium">
                  Potential Dealbreaker
                </span>
              )}
            </div>
            <h2 className="text-xl font-bold text-gray-900">{question.question_text}</h2>
          </div>

          {/* Your Answer */}
          <div className="mb-8">
            <h3 className="font-semibold text-gray-900 mb-3">1. Your Answer</h3>
            {renderAnswerInput(question, answer, setAnswer, false)}
          </div>

          {/* Preferred Partner Answer */}
          <div className="mb-8">
            <h3 className="font-semibold text-gray-900 mb-3">2. Preferred Partner Answer</h3>
            {renderAnswerInput(question, answer, setAnswer, true)}
          </div>

          {/* Importance Level */}
          <div className="mb-6">
            <h3 className="font-semibold text-gray-900 mb-3">3. How important is this to you?</h3>
            <div className="space-y-2">
              {IMPORTANCE_LABELS.map((label, index) => (
                <button
                  key={index}
                  onClick={() => setAnswer({ ...answer, importance: index })}
                  className={`w-full py-3 px-4 rounded-lg border-2 text-left transition-all ${
                    answer.importance === index
                      ? 'border-blue-600 bg-blue-50 text-blue-900'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{label}</span>
                    {index === 4 && (
                      <span className="text-xs text-red-600 font-semibold">Deal Breaker</span>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Deal Breaker Filter Option */}
          {answer.importance === 4 && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <label className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={answer.excludeNonMatching}
                  onChange={(e) => setAnswer({ ...answer, excludeNonMatching: e.target.checked })}
                  className="mt-1 h-5 w-5 text-red-600 rounded"
                />
                <div>
                  <div className="font-medium text-gray-900">
                    Only show me people who match this requirement
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    Profiles that don't match your answer will be completely filtered out from your discovery feed
                  </div>
                </div>
              </label>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex gap-3 pt-6 border-t">
            {currentIndex > 0 && (
              <button
                onClick={handlePrevious}
                className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium"
              >
                Previous
              </button>
            )}
            <button
              onClick={handleSubmit}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-semibold"
            >
              {currentIndex < questions.length - 1 ? 'Save & Continue' : 'Save & Finish'}
            </button>
          </div>
        </div>

        {/* Progress Info */}
        <div className="mt-4 text-center text-sm text-gray-600">
          You can come back and edit your answers anytime from the menu
        </div>
      </div>
    </div>
  );
};

function renderAnswerInput(
  question: CompatibilityQuestion,
  answer: any,
  setAnswer: any,
  isPreferred: boolean
) {
  const textKey = isPreferred ? 'preferredText' : 'text';
  const choiceKey = isPreferred ? 'preferredChoice' : 'choice';
  const numericKey = isPreferred ? 'preferredNumeric' : 'numeric';
  const booleanKey = isPreferred ? 'preferredBoolean' : 'boolean';

  if (question.question_type === 'yes_no') {
    return (
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={() => setAnswer({ ...answer, [booleanKey]: true })}
          className={`py-3 px-4 rounded-lg border-2 font-medium transition-all ${
            answer[booleanKey] === true
              ? 'border-blue-600 bg-blue-50 text-blue-900'
              : 'border-gray-200 hover:border-gray-300'
          }`}
        >
          Yes
        </button>
        <button
          onClick={() => setAnswer({ ...answer, [booleanKey]: false })}
          className={`py-3 px-4 rounded-lg border-2 font-medium transition-all ${
            answer[booleanKey] === false
              ? 'border-blue-600 bg-blue-50 text-blue-900'
              : 'border-gray-200 hover:border-gray-300'
          }`}
        >
          No
        </button>
      </div>
    );
  }

  if (question.question_type === 'multiple_choice' && question.options) {
    return (
      <div className="space-y-2">
        {question.options.map((option) => (
          <button
            key={option}
            onClick={() => setAnswer({ ...answer, [choiceKey]: option })}
            className={`w-full py-3 px-4 rounded-lg border-2 text-left font-medium transition-all ${
              answer[choiceKey] === option
                ? 'border-blue-600 bg-blue-50 text-blue-900'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            {option}
          </button>
        ))}
      </div>
    );
  }

  if (question.question_type === 'scale') {
    return (
      <div>
        <input
          type="range"
          min={question.scale_min}
          max={question.scale_max}
          value={answer[numericKey] ?? question.scale_min}
          onChange={(e) => setAnswer({ ...answer, [numericKey]: parseInt(e.target.value) })}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
        />
        <div className="flex justify-between text-sm text-gray-600 mt-2">
          <span>{question.scale_min_label}</span>
          <span className="font-bold text-blue-600 text-lg">{answer[numericKey] ?? question.scale_min}</span>
          <span>{question.scale_max_label}</span>
        </div>
      </div>
    );
  }

  if (question.question_type === 'text') {
    return (
      <textarea
        value={answer[textKey] || ''}
        onChange={(e) => setAnswer({ ...answer, [textKey]: e.target.value })}
        rows={4}
        className="w-full border-2 border-gray-200 px-4 py-3 rounded-lg focus:border-blue-600 focus:outline-none"
        placeholder="Type your answer here..."
      />
    );
  }

  return null;
}

export default CompatibilityQuestionnairePage;
