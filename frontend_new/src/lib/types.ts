// frontend/src/lib/types.ts

export interface User {
  id: string;
  username?: string;
  email: string;
  createdAt?: string; // ISO date string
  authStatus: 'unauthenticated' | 'authenticating' | 'authenticated' | 'error';
  isLoading: boolean;
  error?: string;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  isCompleted: boolean;
  createdAt: string; // ISO date string
  updatedAt: string; // ISO date string
  dueDate?: string; // ISO date string
  priority: 'low' | 'medium' | 'high';
  userId: string;
}

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

export interface TaskState {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  currentTask: Task | null;
}

export interface TaskCreateData {
  title: string;
  description?: string;
  dueDate?: string;
  priority?: 'low' | 'medium' | 'high';
}

export interface TaskUpdateData {
  title?: string;
  description?: string;
  isCompleted?: boolean;
  dueDate?: string;
  priority?: 'low' | 'medium' | 'high';
}