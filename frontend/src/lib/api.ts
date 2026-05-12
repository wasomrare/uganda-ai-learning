import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import Cookies from 'js-cookie';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'https://uganda-ai-learning-production.up.railway.app/api/v1';

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = Cookies.get('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = Cookies.get('refresh_token');
      if (refresh) {
        try {
          const { data } = await axios.post(`${BASE_URL}/auth/refresh/`, { refresh });
          Cookies.set('access_token', data.access, { expires: 1 });
          original.headers.Authorization = `Bearer ${data.access}`;
          return api(original);
        } catch {
          Cookies.remove('access_token');
          Cookies.remove('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;

export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login/', { username, password }),
  googleLogin: (idToken: string) =>
    api.post('/auth/google/', { id_token: idToken }),
  logout: (refresh: string) =>
    api.post('/auth/logout/', { refresh }),
  me: () => api.get('/auth/me/'),
};

export const studentsApi = {
  list: (params?: Record<string, unknown>) => api.get('/students/', { params }),
  get: (id: string) => api.get(`/students/${id}/`),
  create: (data: unknown) => api.post('/students/', data),
  update: (id: string, data: unknown) => api.patch(`/students/${id}/`, data),
  delete: (id: string) => api.delete(`/students/${id}/`),
  toggleActive: (id: string) => api.post(`/students/${id}/toggle-active/`),
};

export const teachersApi = {
  list: (params?: Record<string, unknown>) => api.get('/teachers/', { params }),
  get: (id: string) => api.get(`/teachers/${id}/`),
  create: (data: unknown) => api.post('/teachers/', data),
  update: (id: string, data: unknown) => api.patch(`/teachers/${id}/`, data),
};

export const classesApi = {
  list: (params?: Record<string, unknown>) => api.get('/classes/', { params }),
  get: (id: string) => api.get(`/classes/${id}/`),
  create: (data: unknown) => api.post('/classes/', data),
  update: (id: string, data: unknown) => api.patch(`/classes/${id}/`, data),
};

export const subjectsApi = {
  list: () => api.get('/subjects/'),
};

export const assessmentsApi = {
  list: (params?: Record<string, unknown>) => api.get('/assessments/', { params }),
  get: (id: string) => api.get(`/assessments/${id}/`),
  create: (data: unknown) => api.post('/assessments/', data),
  update: (id: string, data: unknown) => api.patch(`/assessments/${id}/`, data),
  publish: (id: string) => api.post(`/assessments/${id}/publish/`),
  close: (id: string) => api.post(`/assessments/${id}/close/`),
  results: (id: string) => api.get(`/assessments/${id}/results/`),
};

export const questionsApi = {
  list: (params?: Record<string, unknown>) => api.get('/questions/', { params }),
  create: (data: unknown) => api.post('/questions/', data),
  approve: (id: string) => api.post(`/questions/${id}/approve/`),
  stats: () => api.get('/questions/stats/'),
  generate: (data: unknown) => api.post('/ai/generate/questions/', data),
};

export const analyticsApi = {
  admin: () => api.get('/analytics/admin/'),
  student: (id: string) => api.get(`/analytics/student/${id}/`),
  class: (id: string) => api.get(`/analytics/class/${id}/`),
};

export const dashboardApi = {
  admin: () => api.get('/dashboard/admin/'),
  teacher: () => api.get('/dashboard/teacher/'),
  student: () => api.get('/dashboard/student/'),
};

export const gamificationApi = {
  profile: () => api.get('/gamification/profile/'),
  badges: () => api.get('/gamification/badges/'),
};

export const leaderboardsApi = {
  weekly: (params?: Record<string, unknown>) => api.get('/leaderboards/weekly/', { params }),
};

export const notificationsApi = {
  mine: () => api.get('/notifications/mine/'),
  list: () => api.get('/notifications/mine/'),
  markRead: (id: string) => api.post(`/notifications/${id}/mark-read/`),
  markAllRead: () => api.post('/notifications/mark-all-read/'),
  broadcast: (data: unknown) => api.post('/notifications/broadcast/', data),
};

export const reportsApi = {
  list: () => api.get('/reports/'),
  create: (data: unknown) => api.post('/reports/', data),
};

export const settingsApi = {
  list: () => api.get('/settings/'),
  update: (data: unknown) => api.patch('/settings/', data),
};

export const aiApi = {
  status: () => api.get('/ai/status/'),
  chat: (data: unknown) => api.post('/ai/chat/', data),
  generate: (data: unknown) => api.post('/ai/generate/questions/', data),
};
