import api from './api';

export interface CompatibilityQuestion {
  id: number;
  question_text: string;
  category: string;
  question_type: string;
  options?: string[];
  scale_min?: number;
  scale_max?: number;
  scale_min_label?: string;
  scale_max_label?: string;
  weight: number;
  is_dealbreaker: boolean;
  order_index: number;
}

export interface AnswerSubmit {
  question_id: number;
  // Your answer
  text_answer?: string;
  choice_answer?: string;
  numeric_answer?: number;
  boolean_answer?: boolean;
  // Preferred partner answer
  preferred_text_answer?: string;
  preferred_choice_answer?: string;
  preferred_numeric_answer?: number;
  preferred_boolean_answer?: boolean;
  // Importance: 0=Not Important, 1=Somewhat Important, 2=Important, 3=Very Important, 4=Deal Breaker
  importance?: number;
  // For Deal Breakers: filter out non-matching profiles
  exclude_non_matching?: boolean;
}

export interface CompatibilityAnswer {
  id: number;
  profile_id: number;
  question_id: number;
  // Your answer
  text_answer?: string;
  choice_answer?: string;
  numeric_answer?: number;
  boolean_answer?: boolean;
  // Preferred partner answer
  preferred_text_answer?: string;
  preferred_choice_answer?: string;
  preferred_numeric_answer?: number;
  preferred_boolean_answer?: boolean;
  // Importance level
  importance: number;
  // Filter non-matching
  exclude_non_matching: boolean;
  created_at: string;
}

export interface QuestionnaireProgress {
  total_questions: number;
  answered_questions: number;
  completion_percentage: number;
  is_complete: boolean;
}

export interface CompatibilityScore {
  profile1_id: number;
  profile2_id: number;
  overall_score: number;
  category_scores: Record<string, number>;
  dealbreaker_count: number;
  compatible: boolean;
}

const compatibilityService = {
  getQuestions: async (category?: string): Promise<CompatibilityQuestion[]> => {
    const response = await api.get('/api/v1/compatibility/questions', {
      params: { category },
    });
    return response.data;
  },

  submitAnswer: async (answer: AnswerSubmit): Promise<CompatibilityAnswer> => {
    const response = await api.post('/api/v1/compatibility/answers', answer);
    return response.data;
  },

  getMyAnswers: async (): Promise<CompatibilityAnswer[]> => {
    const response = await api.get('/api/v1/compatibility/answers/me');
    return response.data;
  },

  getProgress: async (): Promise<QuestionnaireProgress> => {
    const response = await api.get('/api/v1/compatibility/progress');
    return response.data;
  },

  getScore: async (otherProfileId: number): Promise<CompatibilityScore> => {
    const response = await api.get(`/api/v1/compatibility/score/${otherProfileId}`);
    return response.data;
  },
};

export default compatibilityService;
