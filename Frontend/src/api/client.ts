/**
 * Aman singh(67401334)
 * Sanmith Kurian (22256557)
 * Yash Agarwal (35564877)
 * Swapnil Nagras (26761683)
 * 
 * API client for communicating with the backend.
 */
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface SoftwareRequest {
  description: string;
  requirements?: string;
}

export interface SoftwareResponse {
  architecture: string;
  code: string;
  tests: string;
  success: boolean;
  message?: string;
}

export interface UsageStats {
  total_api_calls: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_tokens: number;
  agents: Array<{
    agent_name: string;
    total_api_calls: number;
    total_input_tokens: number;
    total_output_tokens: number;
    total_tokens: number;
  }>;
}

export const api = {
  /**
   * Generate software from description and requirements.
   */
  generateSoftware: async (request: SoftwareRequest): Promise<SoftwareResponse> => {
    const response = await apiClient.post<SoftwareResponse>('/api/generate', request);
    return response.data;
  },

  /**
   * Get LLM usage statistics.
   */
  getUsageStats: async (): Promise<UsageStats> => {
    const response = await apiClient.get<UsageStats>('/api/usage');
    return response.data;
  },

  /**
   * Health check.
   */
  healthCheck: async (): Promise<{ status: string; service: string }> => {
    const response = await apiClient.get('/api/health');
    return response.data;
  },
};


