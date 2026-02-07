import { useState, useEffect } from 'react';
import { Task } from '@/lib/types';
import NewTaskItem from './NewTaskItem';

interface TaskListProps {
  tasks: Task[];
  onToggle: (id: string, completed: boolean) => void;
  onDelete: (id: string) => void;
  onEdit: (id: string, updatedTask: Partial<Task>) => void;
  onBulkComplete?: (taskIds: string[]) => void; // Optional callback for bulk completion
}

export default function NewTaskList({ tasks, onToggle, onDelete, onEdit, onBulkComplete }: TaskListProps) {
  const [showCompleted, setShowCompleted] = useState(false);
  const [selectedTasks, setSelectedTasks] = useState<string[]>([]);
  const [selectAllChecked, setSelectAllChecked] = useState(false);

  // Update select-all checkbox state when tasks or selectedTasks change
  useEffect(() => {
    if (tasks.length === 0) {
      setSelectAllChecked(false);
      return;
    }

    const allSelected = tasks.length > 0 && tasks.every(task =>
      selectedTasks.includes(task.id)
    );
    setSelectAllChecked(allSelected);
  }, [tasks, selectedTasks]);

  // Separate completed and active tasks
  const activeTasks = tasks.filter(task => !task.isCompleted);
  const completedTasks = tasks.filter(task => task.isCompleted);

  const handleSelectAllChange = () => {
    if (selectAllChecked) {
      // Deselect all
      setSelectedTasks([]);
    } else {
      // Select all active tasks
      setSelectedTasks(activeTasks.map(task => task.id));
    }
  };

  const handleTaskSelection = (taskId: string, isSelected: boolean) => {
    if (isSelected) {
      setSelectedTasks(prev => [...prev, taskId]);
    } else {
      setSelectedTasks(prev => prev.filter(id => id !== taskId));
    }
  };

  const handleBulkComplete = () => {
    if (onBulkComplete && selectedTasks.length > 0) {
      onBulkComplete(selectedTasks);
      // Clear selection after completing tasks
      setSelectedTasks([]);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      {/* Active Tasks Header */}
      <div className="flex justify-between items-center mb-4 px-2">
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={selectAllChecked}
            onChange={handleSelectAllChange}
            className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
          />
          <label htmlFor="select-all" className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
            Select All
          </label>
        </div>

        {selectedTasks.length > 0 && (
          <button
            onClick={handleBulkComplete}
            className="inline-flex items-center rounded border border-transparent bg-green-600 px-3 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          >
            Mark {selectedTasks.length} as Done
          </button>
        )}
      </div>


      {/* Active Tasks */}
      <div className="mb-8">
        <ul className="divide-y divide-gray-200 dark:divide-gray-700 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
          {activeTasks.map((task) => (
            <NewTaskItem
              key={task.id}
              task={task}
              onToggle={onToggle}
              onDelete={onDelete}
              onEdit={onEdit}
              isSelected={selectedTasks.includes(task.id)}
              onSelectChange={(isSelected) => handleTaskSelection(task.id, isSelected)}
            />
          ))}
        </ul>
      </div>

      {/* Completed Tasks Section */}
      {completedTasks.length > 0 && (
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
          <button
            className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 text-left flex justify-between items-center"
            onClick={() => setShowCompleted(!showCompleted)}
          >
            <span className="font-medium text-gray-700 dark:text-gray-300">Completed ({completedTasks.length})</span>
            <svg
              className={`w-5 h-5 text-gray-500 dark:text-gray-400 transform transition-transform ${showCompleted ? 'rotate-180' : ''
                }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showCompleted && (
            <ul className="divide-y divide-gray-200 dark:divide-gray-700 bg-gray-50 dark:bg-gray-800">
              {completedTasks.map((task) => (
                <NewTaskItem
                  key={task.id}
                  task={task}
                  onToggle={onToggle}
                  onDelete={onDelete}
                  onEdit={onEdit}
                />
              ))}
            </ul>
          )}
        </div>
      )}


      {/* Empty State */}
      {tasks.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">No tasks yet. Add a new task to get started!</p>
        </div>
      )}
    </div>
  );
}