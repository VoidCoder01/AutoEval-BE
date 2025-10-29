/**
 * API Service for Flask Backend Communication
 * Base URL: http://localhost:5000 (proxied via Vite)
 */

import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Hackathon {
  id?: number;
  name: string;
  description: string;
  evaluation_prompt: string;
  criteria?: any[];
  host_email?: string;
  deadline?: string;
  created_at?: string;
}

export interface Submission {
  id?: number;
  hackathon_id: number;
  team_name: string;
  project_name: string;
  code_content?: string;
  documentation_content?: string;
  github_url?: string;
  status?: string;
  created_at?: string;
}

export interface Evaluation {
  id?: number;
  submission_id: number;
  overall_score: number;
  relevance_score: number;
  technical_complexity_score: number;
  creativity_score: number;
  documentation_score: number;
  feedback: string;
  detailed_scores?: string;
  created_at?: string;
}

// Hackathon API
export const hackathonApi = {
  // Get all hackathons
  getAll: async (): Promise<Hackathon[]> => {
    const response = await api.get('/hackathons');
    return response.data;
  },

  // Get single hackathon
  getById: async (id: number): Promise<Hackathon> => {
    const response = await api.get(`/hackathon/${id}`);
    return response.data;
  },

  // Create new hackathon
  create: async (hackathon: Hackathon): Promise<Hackathon> => {
    const response = await api.post('/hackathon', hackathon);
    return response.data;
  },

  // Update hackathon
  update: async (id: number, hackathon: Partial<Hackathon>): Promise<Hackathon> => {
    const response = await api.put(`/hackathon/${id}`, hackathon);
    return response.data;
  },

  // Delete hackathon
  delete: async (id: number): Promise<void> => {
    await api.delete(`/hackathon/${id}`);
  },
};

// Submission API
export const submissionApi = {
  // Get all submissions for a hackathon
  getByHackathon: async (hackathonId: number): Promise<Submission[]> => {
    const response = await api.get(`/hackathon/${hackathonId}/submissions`);
    return response.data;
  },

  // Get single submission
  getById: async (hackathonId: number, submissionId: number): Promise<Submission> => {
    const response = await api.get(`/hackathon/${hackathonId}/submission/${submissionId}`);
    return response.data;
  },

  // Submit with files (multipart/form-data)
  submitWithFiles: async (hackathonId: number, formData: FormData): Promise<Submission> => {
    const response = await api.post(`/hackathon/${hackathonId}/submit`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Submit with GitHub URL
  submitWithGithub: async (hackathonId: number, data: {
    team_name: string;
    project_name: string;
    github_url: string;
  }): Promise<Submission> => {
    const response = await api.post(`/hackathon/${hackathonId}/submit/github`, data);
    return response.data;
  },
};

// Evaluation API
export const evaluationApi = {
  // Get evaluation for a submission
  getBySubmission: async (submissionId: number): Promise<Evaluation> => {
    const response = await api.get(`/submission/${submissionId}/evaluation`);
    return response.data;
  },

  // Get all evaluations for a hackathon (for leaderboard)
  getByHackathon: async (hackathonId: number): Promise<any[]> => {
    const response = await api.get(`/hackathon/${hackathonId}/results`);
    return response.data;
  },

  // Trigger evaluation (if manual trigger is needed)
  triggerEvaluation: async (submissionId: number): Promise<Evaluation> => {
    const response = await api.post(`/submission/${submissionId}/evaluate`);
    return response.data;
  },
};

// Export axios instance for custom requests
export default api;

