import apiClient from './apiClient';

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correct_option: number;
  explanation: string;
}

export interface QuizResponse {
  id: string;
  user_id: string;
  subject: string;
  topic: string;
  questions: QuizQuestion[];
  created_at?: string;
  submitted_at?: string;
  score?: number;
}

export interface QuizSubmissionResult {
  quiz_id: string;
  score: number;
  total: number;
  answers: Record<string, number>;
  correct_answers: Record<string, number>;
  submitted_at: string;
}

export const quizService = {
  async generateQuiz(payload: {
    user_id: string;
    subject: string;
    topic: string;
    question_count: number;
  }): Promise<QuizResponse> {
    const response = await apiClient.post('/quiz/generate', payload);
    return response.data;
  },

  async submitQuiz(
    quizId: string,
    payload: { user_id: string; answers: Record<string, number> }
  ): Promise<QuizSubmissionResult> {
    const response = await apiClient.post(`/quiz/${quizId}/submit`, payload);
    return response.data;
  },
};
