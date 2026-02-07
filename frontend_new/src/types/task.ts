// frontend/src/types/task.ts
export interface Task {
  id: string;
  title: string;
  description?: string;
  isCompleted: boolean;
  createdAt: string;
  updatedAt: string;
  dueDate?: string;
  priority: 'low' | 'medium' | 'high';
  userId: string;
}