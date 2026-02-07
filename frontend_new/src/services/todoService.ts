// frontend/src/services/todoService.ts
import { api } from '@/services/apiClient';

// Helper function to convert snake_case to camelCase
const snakeToCamel = (obj: any): any => {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(snakeToCamel);
  }

  const convertedObj: any = {};
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      // Convert snake_case to camelCase
      const camelKey = key.replace(/_([a-z])/g, (match, letter) => letter.toUpperCase());
      convertedObj[camelKey] = snakeToCamel(obj[key]);
    }
  }
  return convertedObj;
};

// API methods - using the shared api instance to ensure consistent authentication handling
export const todoService = {
  // Get all tasks
  getTasks: async () => {
    try {
      const response = await api.getUserTodos();
      // Transform the response from snake_case to camelCase
      return Array.isArray(response) ? response.map(snakeToCamel) : snakeToCamel(response);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      throw error;
    }
  },

  // Create a new task
  createTask: async (taskData: any) => {
    try {
      const transformedData = {
        title: taskData.title,
        description: taskData.description,
        due_date: taskData.dueDate, // Convert camelCase to snake_case for API
        priority: taskData.priority
      };
      const response = await api.createTodo(transformedData);
      // Transform the response from snake_case to camelCase
      return snakeToCamel(response);
    } catch (error) {
      console.error('Error creating task:', error);
      throw error;
    }
  },

  // Update a task
  updateTask: async (id: string, taskData: any) => {
    try {
      // Convert camelCase to snake_case for API
      const transformedData: any = {};
      for (const key in taskData) {
        if (taskData.hasOwnProperty(key)) {
          // Convert camelCase to snake_case
          const snakeKey = key.replace(/([A-Z])/g, (match) => `_${match.toLowerCase()}`);
          transformedData[snakeKey] = taskData[key];
        }
      }
      const response = await api.updateTodo(id, transformedData);
      // Transform the response from snake_case to camelCase
      return snakeToCamel(response);
    } catch (error) {
      console.error('Error updating task:', error);
      throw error;
    }
  },

  // Delete a task
  deleteTask: async (id: string) => {
    try {
      return await api.deleteTodo(id);
    } catch (error) {
      console.error('Error deleting task:', error);
      throw error;
    }
  },

  // Toggle task completion
  toggleTaskCompletion: async (id: string, isCompleted: boolean) => {
    try {
      const response = await api.updateTodo(id, { is_completed: isCompleted });
      // Transform the response from snake_case to camelCase
      return snakeToCamel(response);
    } catch (error) {
      console.error('Error toggling task completion:', error);
      throw error;
    }
  }
};