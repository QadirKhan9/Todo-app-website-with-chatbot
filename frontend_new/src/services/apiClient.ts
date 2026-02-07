// API Client for Todo AI Chatbot
import axios from 'axios';
import { getStorageItem, setStorageItem, removeStorageItem } from '../utils/storage';

// Base URL from environment variable
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000, // 30 seconds timeout to accommodate AI processing
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
    (config) => {
        // Don't add token for auth endpoints (login, signup, etc.) or if the URL contains /auth/
        const isAuthEndpoint = config.url?.includes('/auth/') || config.url?.includes('/login') || config.url?.includes('/signup');

        if (!isAuthEndpoint) {
            // Get token from wherever it's stored (localStorage, cookie, etc.)
            // Try both 'access_token' and 'token' for backward compatibility
            let token = getStorageItem('access_token');

            if (!token) {
                token = getStorageItem('token');
            }

            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle common errors
apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response?.status === 401) {
            // Dispatch unauthorized event to notify the app
            window.dispatchEvent(new Event('unauthorized'));
        } else if (error.response?.status === 403) {
            // Dispatch forbidden event to notify the app
            window.dispatchEvent(new Event('forbidden'));
        }

        return Promise.reject(error);
    }
);

// API methods
export const api = {
    // Chat operations
    chatWithAI: async (message: string, userId: string | null | undefined = null) => {
        try {
            const requestData: any = {
                message,
                user_id: userId || null  // Pass user_id if available
            };

            // If we don't have a userId, we might need to rely on authentication
            // Only include user_id in the request if it's provided
            if (userId) {
                requestData.user_id = userId;
            }

            const response = await apiClient.post('/v1/chat', requestData);
            return response.data;
        } catch (error) {
            throw handleError(error);
        }
    },

    // Conversation operations
    getConversationMessages: async (conversationId: string) => {
        try {
            const response = await apiClient.get(`/v1/conversations/${conversationId}`);
            return response.data;
        } catch (error) {
            throw handleError(error);
        }
    },

    createConversation: async (initialMessage: string | null = null, userId: string | null = null) => {
        try {
            const requestData: any = {};

            if (initialMessage) {
                requestData.initial_message = initialMessage;
            }

            if (userId) {
                requestData.user_id = userId;
            }

            const response = await apiClient.post('/v1/conversations', requestData);
            return response.data;
        } catch (error) {
            throw handleError(error);
        }
    },

    // Todo operations
    getUserTodos: async () => {
        try {
            const response = await apiClient.get('/api/v1/todos/');
            return response.data;
        } catch (error) {
            throw handleError(error);
        }
    },

    createTodo: async (todoData: any) => {
        try {
            const response = await apiClient.post('/api/v1/todos/', todoData);
            return response.data;
        } catch (error) {
            throw handleError(error);
        }
    },

    updateTodo: async (todoId: string, todoData: any) => {
        try {
            const response = await apiClient.put(`/api/v1/todos/${todoId}`, todoData);
            return response.data;
        } catch (error) {
            throw handleError(error);
        }
    },

    deleteTodo: async (todoId: string) => {
        try {
            const response = await apiClient.delete(`/api/v1/todos/${todoId}`);
            return response.data;
        } catch (error) {
            throw handleError(error);
        }
    }
};

// Helper function to handle errors
function handleError(error: any) {
    if (error.response) {
        // Server responded with error status
        console.error('Server Error:', error.response.data);
        return new Error(`Server Error: ${error.response.data.detail || error.response.statusText}`);
    } else if (error.request) {
        // Request was made but no response received
        console.error('Network Error:', error.request);
        return new Error('Network Error: No response received from server');
    } else {
        // Something else happened
        console.error('Error:', error.message);
        return new Error(`Error: ${error.message}`);
    }
}

// @ts-ignore - Adding methods to axios instance
apiClient.getToken = function () {
    // Try to get token from localStorage first, then from cookie
    let token = getStorageItem('access_token');

    if (!token) {
        token = getStorageItem('token');
    }

    if (!token) {
        // Extract token from cookies if not in localStorage
        const cookieToken = document.cookie
            .split(';')
            .find(cookie => cookie.trim().startsWith('token='));

        if (cookieToken) {
            token = cookieToken.split('=')[1];
        }
    }

    return token;
};

// @ts-ignore
apiClient.setToken = function (token: string) {
    // Store token in localStorage
    setStorageItem('access_token', token);

    // Also store in cookies for server-side access if needed
    const expiryDate = new Date();
    expiryDate.setDate(expiryDate.getDate() + 7); // Token expires in 7 days

    document.cookie = `token=${token}; path=/; expires=${expiryDate.toUTCString()}; SameSite=Strict`;
};

// @ts-ignore
apiClient.removeToken = function () {
    // Remove token from localStorage
    removeStorageItem('access_token');
    removeStorageItem('token');

    // Remove token from cookies as well
    document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict';
};

export default apiClient;
