import { useState } from 'react';
import { Task } from '@/lib/types';
import TaskForm from './TaskForm';

interface TaskItemProps {
  task: Task;
  onToggle: (id: string, completed: boolean) => void;
  onDelete: (id: string) => void;
  onEdit: (id: string, updatedTask: Partial<Task>) => void;
  isSelected?: boolean;
  onSelectChange?: (isSelected: boolean) => void;
}

export default function NewTaskItem({ task, onToggle, onDelete, onEdit, isSelected, onSelectChange }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);

  const handleSave = async (updatedTask: Partial<Task>) => {
    onEdit(task.id, updatedTask);
    setIsEditing(false);
    return Promise.resolve();
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  return (
    <li className={`p-4 flex items-center justify-between ${task.isCompleted ? 'bg-gray-50 dark:bg-gray-800' : 'bg-white dark:bg-gray-800'} hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150`}>
      {isEditing ? (
        <div className="w-full">
          <TaskForm
            initialData={{
              title: task.title,
              description: task.description,
              dueDate: task.dueDate,
              priority: task.priority
            }}
            isEditing={true}
            onSubmit={handleSave}
            onCancel={handleCancel}
          />
        </div>
      ) : (
        <>
          {/* Checkbox for selection */}
          <div className="mr-3">
            <input
              type="checkbox"
              checked={isSelected || task.isCompleted}
              onChange={(e) => {
                if (onSelectChange) {
                  onSelectChange(e.target.checked);
                } else {
                  onToggle(task.id, e.target.checked);
                }
              }}
              className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            />
          </div>

          {/* Left: Task Title */}
          <div className="flex-1 min-w-0">
            <p className={`text-sm font-medium truncate ${task.isCompleted ? 'text-gray-500 dark:text-gray-400 line-through' : 'text-gray-900 dark:text-white'}`}>
              {task.title}
            </p>
            {task.description && (
              <p className={`text-xs text-gray-500 dark:text-gray-400 mt-1 truncate ${task.isCompleted ? 'line-through' : ''}`}>
                {task.description}
              </p>
            )}
          </div>

          {/* Center: Due Date with Clock Icon */}
          {task.dueDate && (
            <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 mx-4">
              <svg
                className="w-4 h-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span>{new Date(task.dueDate).toLocaleDateString()}</span>
            </div>
          )}

          {/* Right: Edit and Delete Icons */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsEditing(true)}
              className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors duration-150"
              aria-label="Edit task"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
            </button>
            <button
              onClick={() => onDelete(task.id)}
              className="text-red-500 hover:text-red-700 transition-colors duration-150"
              aria-label="Delete task"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </>
      )}
    </li>
  );
}