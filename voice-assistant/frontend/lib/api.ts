const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at?: string;
}

export interface SignupData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface ApiError {
  detail: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    // Add auth token if available (check if it's already in headers first)
    if (typeof window !== "undefined" && !config.headers?.Authorization) {
      // Check for admin token first (admin endpoints)
      const adminToken = localStorage.getItem("admin_token");
      const userToken = localStorage.getItem("auth_token");
      
      if (adminToken && endpoint.startsWith("/admin")) {
        config.headers = {
          ...config.headers,
          Authorization: `Bearer ${adminToken}`,
        };
      } else if (userToken) {
        config.headers = {
          ...config.headers,
          Authorization: `Bearer ${userToken}`,
        };
      }
    }

    try {
      const response = await fetch(url, config);
      console.log(`API Response Status: ${response.status}`); // Debug log

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;

        try {
          const errorData: ApiError = await response.json();
          console.log("API Error Data:", errorData); // Debug log
          errorMessage = errorData.detail || errorMessage;
        } catch (parseError) {
          // If we can't parse the error response, use a generic message based on status
          switch (response.status) {
            case 400:
              errorMessage = "Bad request. Please check your input.";
              break;
            case 401:
              errorMessage = "Unauthorized. Please check your credentials.";
              break;
            case 403:
              errorMessage =
                "Forbidden. You don't have permission to perform this action.";
              break;
            case 404:
              errorMessage = "Resource not found.";
              break;
            case 422:
              errorMessage = "Validation error. Please check your input.";
              break;
            case 500:
              errorMessage = "Server error. Please try again later.";
              break;
            default:
              errorMessage = `Server error (${response.status}). Please try again later.`;
          }
        }

        throw new Error(errorMessage);
      }

      return response.json();
    } catch (error) {
      // Handle network errors
      if (error instanceof TypeError && error.message.includes("fetch")) {
        throw new Error(
          "Network error. Please check your connection and try again.",
        );
      }
      throw error;
    }
  }

  // Auth endpoints
  async signup(data: SignupData): Promise<User> {
    return this.request<User>("/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async login(data: LoginData): Promise<AuthResponse> {
    return this.request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // User endpoints
  async getCurrentUser(): Promise<User> {
    // Check if we have an auth token before making the request
    if (!this.isAuthenticated()) {
      throw new Error("Not authenticated");
    }
    return this.request<User>("/users/me");
  }

  async updateUser(data: Partial<User>): Promise<User> {
    return this.request<User>("/users/me", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteUser(): Promise<{ message: string }> {
    return this.request<{ message: string }>("/users/me", {
      method: "DELETE",
    });
  }

  // Resume endpoints
  async uploadResume(
    file: File,
  ): Promise<{ message: string; filename: string; user_id: string }> {
    const formData = new FormData();
    formData.append("file", file);

    const url = `${this.baseUrl}/resume/upload`;
    const token = this.getAuthToken();

    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to upload resume");
    }

    return response.json();
  }

  async getJobMatches(threshold: number = 0.6): Promise<{
    matches: any[];
    total_matches: number;
    threshold: number;
    user_id: string;
  }> {
    return this.request<{
      matches: any[];
      total_matches: number;
      threshold: number;
      user_id: string;
    }>(`/resume/match-jds?threshold=${threshold}`);
  }

  async getJdContent(
    jdFilename: string,
  ): Promise<{ filename: string; content: string }> {
    return this.request<{ filename: string; content: string }>(
      `/resume/jd/${jdFilename}`,
    );
  }

  async getResumeStatus(): Promise<{ has_resume: boolean; user_id: string }> {
    return this.request<{ has_resume: boolean; user_id: string }>(
      "/resume/resume-status",
    );
  }

  // Utility methods
  setAuthToken(token: string) {
    if (typeof window !== "undefined") {
      localStorage.setItem("auth_token", token);
    }
  }

  removeAuthToken() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
    }
  }

  getAuthToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("auth_token");
    }
    return null;
  }

  isAuthenticated(): boolean {
    return !!this.getAuthToken();
  }

  // Admin endpoints
  async adminLogin(username: string, password: string): Promise<{
    access_token: string;
    token_type: string;
    admin_user: any;
  }> {
    const url = `${this.baseUrl}/admin/auth/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`;
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Admin login failed");
    }

    const data = await response.json();
    this.setAdminToken(data.access_token);
    return data;
  }

  async adminSignup(
    username: string,
    email: string,
    password: string,
  ): Promise<any> {
    return this.request<any>("/admin/auth/signup", {
      method: "POST",
      body: JSON.stringify({ username, email, password }),
    });
  }

  setAdminToken(token: string) {
    if (typeof window !== "undefined") {
      localStorage.setItem("admin_token", token);
    }
  }

  removeAdminToken() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("admin_token");
    }
  }

  getAdminToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("admin_token");
    }
    return null;
  }

  isAdminAuthenticated(): boolean {
    return !!this.getAdminToken();
  }

  // Admin stats endpoints
  async getAdminOverviewStats(): Promise<any> {
    return this.request<any>("/admin/stats/overview");
  }

  async getAdminPipelineStats(): Promise<any> {
    return this.request<any>("/admin/stats/pipeline");
  }

  async getAdminSystemHealth(): Promise<any> {
    return this.request<any>("/admin/stats/health");
  }

  async getScoreDistribution(): Promise<any> {
    return this.request<any>("/admin/stats/score-distribution");
  }

  async getQuestionPerformance(): Promise<any> {
    return this.request<any>("/admin/analytics/question-performance");
  }

  // Admin user management
  async getAllUsers(params?: {
    skip?: number;
    limit?: number;
    search?: string;
  }): Promise<any[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.append("skip", params.skip.toString());
    if (params?.limit) queryParams.append("limit", params.limit.toString());
    if (params?.search) queryParams.append("search", params.search);

    const query = queryParams.toString();
    return this.request<any[]>(`/admin/users${query ? `?${query}` : ""}`);
  }

  async getUserDetails(userId: number): Promise<any> {
    return this.request<any>(`/admin/users/${userId}`);
  }

  // Admin interview management
  async getAllInterviews(params?: {
    skip?: number;
    limit?: number;
    user_id?: number;
    min_score?: number;
    max_score?: number;
  }): Promise<any[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.append("skip", params.skip.toString());
    if (params?.limit) queryParams.append("limit", params.limit.toString());
    if (params?.user_id)
      queryParams.append("user_id", params.user_id.toString());
    if (params?.min_score)
      queryParams.append("min_score", params.min_score.toString());
    if (params?.max_score)
      queryParams.append("max_score", params.max_score.toString());

    const query = queryParams.toString();
    return this.request<any[]>(`/admin/interviews${query ? `?${query}` : ""}`);
  }

  async getInterviewDetails(sessionId: string): Promise<any> {
    return this.request<any>(`/admin/interviews/${sessionId}`);
  }

  // Admin analytics
  async getUserRankings(params?: {
    sort_by?: string;
    limit?: number;
    min_interviews?: number;
  }): Promise<any> {
    const queryParams = new URLSearchParams();
    if (params?.sort_by) queryParams.append("sort_by", params.sort_by);
    if (params?.limit) queryParams.append("limit", params.limit.toString());
    if (params?.min_interviews)
      queryParams.append("min_interviews", params.min_interviews.toString());

    const query = queryParams.toString();
    return this.request<any>(
      `/admin/analytics/user-rankings${query ? `?${query}` : ""}`,
    );
  }

  async compareUsers(userIds: number[]): Promise<any> {
    return this.request<any>("/admin/analytics/compare-users", {
      method: "POST",
      body: JSON.stringify(userIds),
    });
  }

  async getTopPerformers(params?: {
    limit?: number;
    min_interviews?: number;
  }): Promise<any> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append("limit", params.limit.toString());
    if (params?.min_interviews)
      queryParams.append("min_interviews", params.min_interviews.toString());

    const query = queryParams.toString();
    return this.request<any>(
      `/admin/analytics/top-performers${query ? `?${query}` : ""}`,
    );
  }

  async getTranscriptStatus(): Promise<any> {
    return this.request<any>("/admin/interviews/transcript-status");
  }

  async getRecentActivity(limit: number = 10): Promise<any[]> {
    return this.request<any[]>(`/admin/activity/recent?limit=${limit}`);
  }

  // JD Management endpoints
  async createJD(data: {
    title: string;
    description?: string;
    content: string;
    requirements?: any;
  }): Promise<any> {
    return this.request<any>("/jds", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async uploadJDFile(
    file: File,
    title: string,
    description?: string
  ): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);
    if (description) formData.append("description", description);

    const url = `${this.baseUrl}/jds/upload`;
    const token = this.getAdminToken();

    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to upload JD");
    }

    return response.json();
  }

  async getAllJDs(params?: {
    skip?: number;
    limit?: number;
  }): Promise<any[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.append("skip", params.skip.toString());
    if (params?.limit) queryParams.append("limit", params.limit.toString());

    const query = queryParams.toString();
    return this.request<any[]>(`/jds${query ? `?${query}` : ""}`);
  }

  async getJD(jdId: number): Promise<any> {
    return this.request<any>(`/jds/${jdId}`);
  }

  async updateJD(jdId: number, data: Partial<any>): Promise<any> {
    return this.request<any>(`/jds/${jdId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteJD(jdId: number): Promise<void> {
    return this.request<void>(`/jds/${jdId}`, {
      method: "DELETE",
    });
  }

  async createJDVersion(
    jdId: number,
    data: {
      version_number: number;
      content: string;
      requirements?: any;
      is_active?: boolean;
    }
  ): Promise<any> {
    return this.request<any>(`/jds/${jdId}/versions`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async activateJDVersion(jdId: number, versionId: number): Promise<any> {
    return this.request<any>(`/jds/${jdId}/versions/${versionId}/activate`, {
      method: "PATCH",
    });
  }

  async reopenJD(jdId: number): Promise<any> {
    return this.request<any>(`/jds/${jdId}/reopen`, {
      method: "PATCH",
    });
  }

  // Export and matching endpoints
  async exportInterviews(format: "csv" | "json" = "csv"): Promise<Blob> {
    const url = `${this.baseUrl}/admin/interviews/export?format=${format}`;
    const token = this.getAdminToken();

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      let errorMessage = "Failed to export interviews";
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        // If response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    return response.blob();
  }

  async runRematchAll(): Promise<any> {
    return this.request<any>("/admin/matching/rematch-all", {
      method: "POST",
    });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
