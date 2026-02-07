// frontend/src/components/TaskForm.tsx
import { useState, useEffect } from 'react';
import { TaskCreateData } from '@/lib/types';

interface TaskFormProps {
  onSubmit: (taskData: TaskCreateData) => Promise<any>;
  onCancel?: () => void;
  initialData?: Partial<TaskCreateData>;
  isEditing?: boolean;
}

export default function TaskForm({ onSubmit, onCancel, initialData, isEditing = false }: TaskFormProps) {
  const [title, setTitle] = useState(initialData?.title || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [dueDate, setDueDate] = useState(initialData?.dueDate || '');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>(initialData?.priority || 'medium');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  // Trigger animation when component mounts
  useEffect(() => {
    setIsVisible(true);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');
    setIsSubmitting(true);

    // Validation
    if (!title.trim()) {
      setError('Title is required');
      setIsSubmitting(false);
      return;
    }

    if (title.length > 200) {
      setError('Title must be 200 characters or less');
      setIsSubmitting(false);
      return;
    }

    if (description && description.length > 1000) {
      setError('Description must be 1000 characters or less');
      setIsSubmitting(false);
      return;
    }

    // Submit the task data
    try {
      const result = await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
        dueDate: dueDate || undefined,
        priority: priority as 'low' | 'medium' | 'high'
      });

      // If the submission was successful, show success message
      if (result && result.success) {
        setSuccessMessage('Task created successfully!');

        // Clear the form after successful submission (for create only)
        if (!initialData) {
          setTimeout(() => {
            setTitle('');
            setDescription('');
            setDueDate('');
            setPriority('medium');
          }, 500);
        }
      } else if (result && result.error) {
        setError(result.error);
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while submitting the task.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className={`
        bg-white dark:bg-gray-800 rounded-lg p-4 sm:p-6 shadow-lg
        transition-all duration-300 ease-in-out
        ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}
        border border-gray-200 dark:border-gray-700
      `}
    >
      <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4 transition-colors duration-300">
        {initialData ? 'Edit Task' : 'Create New Task'}
      </h2>

      {error && (
        <div
          className="
            mb-4 rounded-md bg-red-50 dark:bg-red-900/20 p-4
            animate-pulse
            border-l-4 border-red-500
          "
        >
          <div className="text-sm text-red-700 dark:text-red-300 flex items-center">
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            {error}
          </div>
        </div>
      )}

      {successMessage && (
        <div
          className="
            mb-4 rounded-md bg-green-50 dark:bg-green-900/20 p-4
            border-l-4 border-green-500
            transform transition-all duration-300
          "
        >
          <div className="text-sm text-green-700 dark:text-green-300 flex items-center">
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            {successMessage}
          </div>
        </div>
      )}

      <div className="space-y-4">
        <div className="transition-all duration-300 hover:scale-[1.01]">
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Title *
          </label>
          <div className="relative">
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="
                mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm
                focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white
                sm:text-sm transition-all duration-300
                focus:ring-2 focus:ring-opacity-50
                pl-3 pr-3 py-2
              "
              placeholder="Task title"
              maxLength={200}
            />
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
              <span className="text-gray-400 text-sm">
                {title.length}/200
              </span>
            </div>
          </div>
        </div>

        <div className="transition-all duration-300 hover:scale-[1.01]">
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Description
          </label>
          <div className="relative">
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="
                mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm
                focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white
                sm:text-sm transition-all duration-300
                focus:ring-2 focus:ring-opacity-50
                pl-3 pr-3 py-2
              "
              placeholder="Task description (optional)"
              maxLength={1000}
            />
            <div className="absolute bottom-2 right-3 flex items-center pointer-events-none">
              <span className="text-gray-400 text-xs">
                {description.length}/1000
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="transition-all duration-300 hover:scale-[1.01]">
            <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Due Date
            </label>
            <input
              type="date"
              id="dueDate"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="
                mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600
                shadow-sm focus:border-indigo-500 focus:ring-indigo-500
                dark:bg-gray-700 dark:text-white sm:text-sm transition-all duration-300
                focus:ring-2 focus:ring-opacity-50
                pl-3 pr-3 py-2
              "
            />
          </div>

          <div className="transition-all duration-300 hover:scale-[1.01]">
            <label htmlFor="priority" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Priority
            </label>
            <div className="relative">
              <select
                id="priority"
                value={priority}
                onChange={(e) => setPriority(e.target.value as 'low' | 'medium' | 'high')}
                className="
                  mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600
                  bg-white dark:bg-gray-700 shadow-sm focus:border-indigo-500
                  focus:ring-indigo-500 sm:text-sm transition-all duration-300
                  focus:ring-2 focus:ring-opacity-50
                  appearance-none pl-3 pr-8 py-2
                "
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700 dark:text-gray-300">
                <svg className="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              disabled={isSubmitting}
              className="
                inline-flex items-center rounded border border-gray-300 bg-white
                px-4 py-2 text-sm font-medium text-gray-700 shadow-sm
                hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500
                dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200
                dark:hover:bg-gray-600 transition-all duration-200
                disabled:opacity-50 disabled:cursor-not-allowed
              "
            >
              Cancel
            </button>
          )}
          <button
            type="submit"
            disabled={isSubmitting}
            className={`
              inline-flex items-center rounded border border-transparent
              px-4 py-2 text-sm font-medium text-white shadow-sm
              focus:outline-none focus:ring-2 focus:ring-offset-2
              transition-all duration-200 transform hover:scale-105
              ${isSubmitting
                ? 'bg-indigo-400 dark:bg-indigo-400 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600'
              }
              focus:ring-indigo-500 focus:ring-offset-2
            `}
          >
            {isSubmitting ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {initialData ? 'Updating...' : 'Creating...'}
              </>
            ) : (
              <>
                <svg
                  className="-ml-1 mr-2 h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d={initialData ? "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" : "M12 6v6m0 0v6m0-6h6m-6 0H6"}
                  />
                </svg>
                {initialData ? 'Update Task' : 'Create Task'}
              </>
            )}
          </button>
        </div>
      </div>
    </form>
  );
}