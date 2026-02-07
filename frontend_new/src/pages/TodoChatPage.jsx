import React, { useState, useEffect } from 'react';
import ChatInterface from '../components/ChatInterface';
import NewTaskList from '../components/NewTaskList';
import { api } from '../services/apiClient';
import { useTasks } from '../hooks/useTasks';

const TodoChatPage = () => {
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(true);

  // Mock user ID - in a real app, this would come from authentication
  useEffect(() => {
    // Simulate getting user ID from auth
    setTimeout(() => {
      setUserId('user-123');
      setLoading(false);
    }, 500);
  }, []);

  // Using the same hook as the dashboard
  const {
    tasks: todos,
    isLoading: tasksLoading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleTaskCompletion,
  } = useTasks(userId);

  // Fetch user's todos when component mounts or user ID changes
  useEffect(() => {
    if (userId) {
      fetchTasks();
    }
  }, [userId, fetchTasks]);

  const handleToggleTask = async (id, completed) => {
    await toggleTaskCompletion(id, completed);
  };

  const handleDeleteTask = async (id) => {
    await deleteTask(id);
  };

  const handleUpdateTask = async (id, updatedData) => {
    await updateTask(id, updatedData);
  };

  const handleBulkComplete = async (taskIds) => {
    // Update all selected tasks to completed
    for (const taskId of taskIds) {
      await toggleTaskCompletion(taskId, true);
    }
  };

  if (loading || tasksLoading) {
    return <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 dark:border-indigo-400"></div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4 md:p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Todo AI Chatbot</h1>
      </header>

      <main className="main-content max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column - Task list */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-6">Your Todos</h2>

              {error && (
                <div className="rounded-md bg-red-50 dark:bg-red-900/20 p-4 mb-4">
                  <div className="text-sm text-red-700 dark:text-red-300">
                    {error}
                  </div>
                </div>
              )}

              <NewTaskList
                tasks={todos}
                onToggle={handleToggleTask}
                onDelete={handleDeleteTask}
                onEdit={handleUpdateTask}
                onBulkComplete={handleBulkComplete}
              />
            </div>
          </div>

          {/* Right column - Chat interface */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 sticky top-6">
              <ChatInterface onTaskUpdate={fetchTasks} />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default TodoChatPage;