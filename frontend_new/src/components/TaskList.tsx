// frontend/src/components/TaskList.tsx
import { useState, useEffect } from 'react';
import { Task } from '@/lib/types';
import TaskItem from './TaskItem';

interface TaskListProps {
  tasks: Task[];
  onToggle: (id: string, completed: boolean) => void;
  onDelete: (id: string) => void;
  onEdit: (id: string, updatedTask: Partial<Task>) => void;
  onBulkComplete?: (taskIds: string[]) => void; // Optional callback for bulk completion
}

export default function TaskList({ tasks, onToggle, onDelete, onEdit, onBulkComplete }: TaskListProps) {
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

  const handleSelectAllChange = () => {
    if (selectAllChecked) {
      // Deselect all
      setSelectedTasks([]);
    } else {
      // Select all
      setSelectedTasks(tasks.map(task => task.id));
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

  if (tasks.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No tasks yet. Add a new task to get started!</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden bg-white shadow sm:rounded-md">
      <div className="border-b border-gray-200 bg-white px-4 py-5 sm:px-6 flex justify-between items-center">
        <div className="flex items-center">
          <input
            type="checkbox"
            checked={selectAllChecked}
            onChange={handleSelectAllChange}
            className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
          />
          <label htmlFor="select-all" className="ml-2 text-sm font-medium text-gray-700">
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

      <ul className="divide-y divide-gray-200">
        {tasks.map((task) => (
          <TaskItem
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
  );
}