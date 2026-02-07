import React from 'react';

interface QuickActionButtonsProps {
  onActionClick: (action: string) => void;
  disabled?: boolean;
}

const QuickActionButtons: React.FC<QuickActionButtonsProps> = ({ onActionClick, disabled = false }) => {
  const actions = [
    { id: 'create-task', label: 'Create Task', icon: '📝', description: 'Add a new task' },
    { id: 'view-tasks', label: 'View Tasks', icon: '📋', description: 'See your task list' },
    { id: 'complete-task', label: 'Complete Task', icon: '✅', description: 'Mark a task as done' },
    { id: 'update-task', label: 'Update Task', icon: '🔄', description: 'Modify a task' },
    { id: 'delete-task', label: 'Delete Task', icon: '🗑️', description: 'Remove a task' },
  ];

  return (
    <div className="flex flex-wrap gap-1.5 p-1.5 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
      {actions.map((action) => (
        <button
          key={action.id}
          onClick={() => onActionClick(action.id)}
          disabled={disabled}
          className="flex flex-col items-center justify-center p-1.5 bg-white dark:bg-gray-700 rounded-md border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed min-w-[55px] focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
          title={action.description}
        >
          <span className="text-base">{action.icon}</span>
          <span className="text-[10px] mt-0.5 text-gray-700 dark:text-gray-300">{action.label}</span>
        </button>
      ))}
    </div>
  );
};

export default QuickActionButtons;