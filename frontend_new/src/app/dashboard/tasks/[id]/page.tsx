// frontend/src/app/dashboard/tasks/[id]/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useTasks } from '@/hooks/useTasks';
import { useAuth } from '@/components/AuthProvider';
import TaskForm from '@/components/TaskForm';
import { Task } from '@/lib/types';

export default function TaskDetailPage() {
  const { id: taskId } = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const {
    tasks,
    isLoading,
    error,
    updateTask,
    deleteTask,
    toggleTaskCompletion
  } = useTasks(user?.id || '');

  const [task, setTask] = useState<Task | null>(null);
  const [showEditForm, setShowEditForm] = useState(false);

  useEffect(() => {
    if (tasks.length > 0 && taskId) {
      const foundTask = tasks.find(t => t.id === taskId);
      if (foundTask) {
        setTask(foundTask);
      } else {
        // Task not found in current list, might need to fetch directly
        router.push('/dashboard');
      }
    }
  }, [tasks, taskId, router]);

  const handleToggleCompletion = async () => {
    if (task && user?.id) {
      await toggleTaskCompletion(task.id, !task.isCompleted);
      // The task state will be updated via the hook
    }
  };

  const handleDelete = async () => {
    if (task && user?.id) {
      if (window.confirm('Are you sure you want to delete this task?')) {
        await deleteTask(task.id);
        router.push('/dashboard');
      }
    }
  };

  const handleUpdate = async (updatedData: Partial<Task>) => {
    if (task && user?.id) {
      await updateTask(task.id, updatedData);
      setShowEditForm(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="rounded-md bg-red-50 p-4">
          <div className="text-sm text-red-700">{error}</div>
        </div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg">Task not found</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-start">
            <button
              onClick={() => router.back()}
              className="inline-flex items-center text-indigo-600 hover:text-indigo-900"
            >
              ← Back to tasks
            </button>
            <div className="flex space-x-2">
              <button
                onClick={() => setShowEditForm(true)}
                className="inline-flex items-center rounded border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                Edit
              </button>
              <button
                onClick={handleDelete}
                className="inline-flex items-center rounded border border-transparent bg-red-600 px-3 py-1.5 text-sm font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
              >
                Delete
              </button>
            </div>
          </div>

          {showEditForm ? (
            <div className="mt-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Edit Task</h2>
              <TaskForm
                onSubmit={handleUpdate}
                onCancel={() => setShowEditForm(false)}
                initialData={{
                  title: task.title,
                  description: task.description,
                  dueDate: task.dueDate,
                  priority: task.priority
                }}
              />
            </div>
          ) : (
            <div className="mt-6">
              <div className="flex items-start">
                <input
                  type="checkbox"
                  checked={task.isCompleted}
                  onChange={handleToggleCompletion}
                  className="h-5 w-5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 mt-1"
                />
                <div className="ml-3">
                  <h1 className={`text-2xl font-bold ${task.isCompleted ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                    {task.title}
                  </h1>
                  {task.description && (
                    <p className={`mt-4 text-gray-700 ${task.isCompleted ? 'line-through' : ''}`}>
                      {task.description}
                    </p>
                  )}
                </div>
              </div>

              <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-900">Status</h3>
                  <div className="mt-2">
                    <span className={`inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium ${
                      task.isCompleted
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {task.isCompleted ? 'Completed' : 'Pending'}
                    </span>
                  </div>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-900">Priority</h3>
                  <div className="mt-2">
                    <span className={`inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium ${
                      task.priority === 'high'
                        ? 'bg-red-100 text-red-800'
                        : task.priority === 'medium'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-green-100 text-green-800'
                    }`}>
                      {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                    </span>
                  </div>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-900">Created</h3>
                  <div className="mt-1 text-sm text-gray-900">
                    {new Date(task.createdAt).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </div>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-gray-900">Due Date</h3>
                  <div className="mt-1 text-sm text-gray-900">
                    {task.dueDate
                      ? new Date(task.dueDate).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })
                      : 'No due date'}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}