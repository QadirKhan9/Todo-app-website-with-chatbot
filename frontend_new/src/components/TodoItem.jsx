import React from 'react';

const TodoItem = ({ todo, onToggleComplete, onDelete }) => {
  const handleToggle = () => {
    onToggleComplete(todo.id, todo.status);
  };

  const handleDelete = () => {
    if (window.confirm(`Are you sure you want to delete "${todo.title}"?`)) {
      onDelete(todo.id);
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'completed':
        return 'status-completed';
      case 'in_progress':
        return 'status-in-progress';
      case 'pending':
      default:
        return 'status-pending';
    }
  };

  const getPriorityClass = (priority) => {
    switch (priority) {
      case 'high':
        return 'priority-high';
      case 'medium':
        return 'priority-medium';
      case 'low':
        return 'priority-low';
      default:
        return 'priority-medium';
    }
  };

  return (
    <div className={`todo-item ${getStatusClass(todo.status)}`}>
      <div className="todo-header">
        <input
          type="checkbox"
          checked={todo.status === 'completed'}
          onChange={handleToggle}
          className="todo-checkbox"
        />
        <span className={`todo-title ${todo.status === 'completed' ? 'completed' : ''}`}>
          {todo.title}
        </span>
        <button onClick={handleDelete} className="delete-button" aria-label="Delete todo">
          ×
        </button>
      </div>
      
      <div className="todo-details">
        {todo.description && <p className="todo-description">{todo.description}</p>}
        <div className="todo-meta">
          <span className={`priority-badge ${getPriorityClass(todo.priority)}`}>
            {todo.priority.charAt(0).toUpperCase() + todo.priority.slice(1)}
          </span>
          {todo.due_date && (
            <span className="due-date">
              Due: {new Date(todo.due_date).toLocaleDateString()}
            </span>
          )}
          <span className={`status-badge ${getStatusClass(todo.status)}`}>
            {todo.status.replace('_', ' ').charAt(0).toUpperCase() + todo.status.slice(1)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default TodoItem;