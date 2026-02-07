import React, { useState, useEffect } from 'react';
import TodoItem from './TodoItem'; // We'll create this next
import { api } from '../services/apiClient';

const TodoList = ({ todos, onRefresh }) => {
  const [localTodos, setLocalTodos] = useState(todos || []);
  const [newTodoTitle, setNewTodoTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Update local todos when prop changes
  useEffect(() => {
    setLocalTodos(todos || []);
  }, [todos]);

  const handleAddTodo = async (e) => {
    e.preventDefault();

    if (!newTodoTitle.trim()) return;

    setLoading(true);
    setError(null);

    try {
      await api.createTodo({ title: newTodoTitle });
      setNewTodoTitle('');

      // Refresh the list
      if (onRefresh) {
        await onRefresh();
      }
    } catch (err) {
      setError(err.message);
      console.error('Error adding todo:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleComplete = async (todoId, currentStatus) => {
    setLoading(true);
    setError(null);

    try {
      const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';

      await api.updateTodo(todoId, { status: newStatus });

      // Refresh the list
      if (onRefresh) {
        await onRefresh();
      }
    } catch (err) {
      setError(err.message);
      console.error('Error updating todo:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTodo = async (todoId) => {
    setLoading(true);
    setError(null);

    try {
      await api.deleteTodo(todoId);

      // Refresh the list
      if (onRefresh) {
        await onRefresh();
      }
    } catch (err) {
      setError(err.message);
      console.error('Error deleting todo:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="todo-list">
      <form onSubmit={handleAddTodo} className="add-todo-form">
        <input
          type="text"
          value={newTodoTitle}
          onChange={(e) => setNewTodoTitle(e.target.value)}
          placeholder="Add a new todo..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !newTodoTitle.trim()}>
          {loading ? 'Adding...' : 'Add'}
        </button>
      </form>

      {error && <div className="error-message">Error: {error}</div>}

      <div className="todos">
        {localTodos.length === 0 ? (
          <p>No todos yet. Add one above!</p>
        ) : (
          localTodos.map((todo) => (
            <TodoItem
              key={todo.id}
              todo={todo}
              onToggleComplete={handleToggleComplete}
              onDelete={handleDeleteTodo}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default TodoList;