// frontend/src/components/TaskItem.tsx
import { useState } from 'react';
import { Task } from '@/lib/types';

interface TaskItemProps {
  task: Task;
  onToggle: (id: string, completed: boolean) => void;
  onDelete: (id: string) => void;
  onEdit: (id: string, updatedTask: Partial<Task>) => void;
  isSelected?: boolean;
  onSelectChange?: (isSelected: boolean) => void;
}

export default function TaskItem({ task, onToggle, onDelete, onEdit, isSelected, onSelectChange }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || '');
  const [editPriority, setEditPriority] = useState(task.priority);

  const handleSave = () => {
    onEdit(task.id, {
      title: editTitle,
      description: editDescription,
      priority: editPriority
    });
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditTitle(task.title);
    setEditDescription(task.description || '');
    setEditPriority(task.priority);
    setIsEditing(false);
  };

  return (
    <li className={`relative flex items-start p-4 hover:bg-gray-50 ${task.isCompleted ? 'bg-green-50' : ''}`}>
      <div className="flex items-start">
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
          className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 mt-1"
        />
        <div className="min-w-0 flex-1 pl-3">
          {isEditing ? (
            <div className="space-y-3">
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                autoFocus
              />
              <textarea
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                rows={2}
              />
              <select
                value={editPriority}
                onChange={(e) => setEditPriority(e.target.value as 'low' | 'medium' | 'high')}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
              <div className="flex space-x-2">
                <button
                  onClick={handleSave}
                  className="inline-flex items-center rounded border border-transparent bg-indigo-600 px-2.5 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                >
                  Save
                </button>
                <button
                  onClick={handleCancel}
                  className="inline-flex items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div>
              <p className={`text-sm font-medium text-gray-900 ${task.isCompleted ? 'line-through' : ''}`}>
                {task.title}
              </p>
              {task.description && (
                <p className={`text-sm text-gray-500 mt-1 ${task.isCompleted ? 'line-through' : ''}`}>
                  {task.description}
                </p>
              )}
              <div className="mt-2 flex items-center text-xs text-gray-500">
                <span>Priority: {task.priority}</span>
                {task.dueDate && (
                  <>
                    <span className="mx-2">•</span>
                    <span>Due: {new Date(task.dueDate).toLocaleDateString()}</span>
                  </>
                )}
                <span className="mx-2">•</span>
                <span>Created: {new Date(task.createdAt).toLocaleDateString()}</span>
              </div>
            </div>
          )}
        </div>
        {!isEditing && (
          <div className="flex space-x-2">
            <button
              onClick={() => setIsEditing(true)}
              className="inline-flex items-center rounded border border-gray-300 bg-white px-2.5 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              Edit
            </button>
            <button
              onClick={() => onDelete(task.id)}
              className="inline-flex items-center rounded border border-transparent bg-red-600 px-2.5 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            >
              Delete
            </button>
          </div>
        )}
      </div>
    </li>
  );
}