import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import compatibilityService, { CompatibilityQuestion, AnswerSubmit, QuestionnaireProgress } from '../services/compatibilityService';

const CompatibilityQuestionnairePage: React.FC = () => {
  const [questions, setQuestions] = useState<CompatibilityQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [progress, setProgress] = useState<QuestionnaireProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const [answer, setAnswer] = useState<{
    text?: string;
    choice?: string;
    numeric?: number;
    boolean?: boolean;
    importance: number;
  }>({
    importance: 5,
  });

  useEffect(() => {
    loadQuestions();
    loadProgress();
  }, []);

  const loadQuestions = async () => {
    try {
      const data = await compatibilityService.getQuestions();
      setQuestions(data);
    } catch (error) {
      console.error('Error loading questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadProgress = async () => {
    try {
      const data = await compatibilityService.getProgress();
      setProgress(data);
    } catch (error) {
      console.error('Error loading progress:', error);
    }
  };

  const handleSubmit = async () => {
    const question = questions[currentIndex];
    const answerData: AnswerSubmit = {
      question_id: question.id,
      importance: answer.importance,
    };

    if (question.question_type === 'text') {
      answerData.text_answer = answer.text;
    } else if (question.question_type === 'multiple_choice') {
      answerData.choice_answer = answer.choice;
    } else if (question.question_type === 'scale') {
      answerData.numeric_answer = answer.numeric;
    } else if (question.question_type === 'yes_no') {
      answerData.boolean_answer = answer.boolean;
    }

    try {
      await compatibilityService.submitAnswer(answerData);
      
      // Reset answer
      setAnswer({ importance: 5 });
      
      // Move to next question or finish
      if (currentIndex < questions.length - 1) {
        setCurrentIndex(currentIndex + 1);
      } else {
        navigate('/discovery');
      }
      
      await loadProgress();
    } catch (error) {
      console.error('Error submitting answer:', error);
    }
  };

  const handleSkip = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setAnswer({ importance: 5 });
    } else {
      navigate('/discovery');
    }
  };

  if (loading) return <div className="p-8">Loading questions...</div>;
  if (questions.length === 0) return <div className="p-8">No questions available.</div>;

  const question = questions[currentIndex];

  return (
    <div className="max-w-2xl mx-auto p-8">
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h1 className="text-2xl font-bold">Compatibility Questionnaire</h1>
          <span className="text-sm text-gray-600">
            Question {currentIndex + 1} of {questions.length}
          </span>
        </div>
        {progress && (
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${progress.completion_percentage}%` }}
            />
          </div>
        )}
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <div className="mb-4">
          <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mb-2">
            {question.category}
          </span>
          {question.is_dealbreaker && (
            <span className="inline-block bg-red-100 text-red-800 text-xs px-2 py-1 rounded mb-2 ml-2">
              Dealbreaker
            </span>
          )}
        </div>

        <h2 className="text-xl font-semibold mb-6">{question.question_text}</h2>

        {question.question_type === 'yes_no' && (
          <div className="space-y-2">
            <button
              onClick={() => setAnswer({ ...answer, boolean: true })}
              className={`w-full py-3 px-4 rounded border ${
                answer.boolean === true ? 'bg-blue-600 text-white' : 'bg-white'
              }`}
            >
              Yes
            </button>
            <button
              onClick={() => setAnswer({ ...answer, boolean: false })}
              className={`w-full py-3 px-4 rounded border ${
                answer.boolean === false ? 'bg-blue-600 text-white' : 'bg-white'
              }`}
            >
              No
            </button>
          </div>
        )}

        {question.question_type === 'multiple_choice' && question.options && (
          <div className="space-y-2">
            {question.options.map((option) => (
              <button
                key={option}
                onClick={() => setAnswer({ ...answer, choice: option })}
                className={`w-full py-3 px-4 rounded border text-left ${
                  answer.choice === option ? 'bg-blue-600 text-white' : 'bg-white'
                }`}
              >
                {option}
              </button>
            ))}
          </div>
        )}

        {question.question_type === 'scale' && (
          <div>
            <input
              type="range"
              min={question.scale_min}
              max={question.scale_max}
              value={answer.numeric || question.scale_min}
              onChange={(e) => setAnswer({ ...answer, numeric: parseInt(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-600">
              <span>{question.scale_min_label}</span>
              <span className="font-semibold">{answer.numeric || question.scale_min}</span>
              <span>{question.scale_max_label}</span>
            </div>
          </div>
        )}

        {question.question_type === 'text' && (
          <textarea
            value={answer.text || ''}
            onChange={(e) => setAnswer({ ...answer, text: e.target.value })}
            rows={4}
            className="w-full border px-3 py-2 rounded"
            placeholder="Your answer..."
          />
        )}

        <div className="mt-6">
          <label className="block text-sm font-medium mb-2">
            How important is this to you? (1-10)
          </label>
          <input
            type="range"
            min={1}
            max={10}
            value={answer.importance}
            onChange={(e) => setAnswer({ ...answer, importance: parseInt(e.target.value) })}
            className="w-full"
          />
          <div className="text-center text-sm text-gray-600">{answer.importance}</div>
        </div>

        <div className="mt-8 flex gap-4">
          <button
            onClick={handleSubmit}
            className="flex-1 bg-blue-600 text-white py-3 rounded hover:bg-blue-700"
          >
            {currentIndex < questions.length - 1 ? 'Next' : 'Finish'}
          </button>
          <button
            onClick={handleSkip}
            className="px-6 py-3 border rounded hover:bg-gray-100"
          >
            Skip
          </button>
        </div>
      </div>
    </div>
  );
};

export default CompatibilityQuestionnairePage;
