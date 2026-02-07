// frontend/src/app/dashboard/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useTasks } from "@/hooks/useTasks";
import { useAuth } from "@/components/AuthProvider";
import NewTaskList from "@/components/NewTaskList";
import TaskForm from "@/components/TaskForm";
import { TaskCreateData } from "@/lib/types";
import ThemeToggle from "@/components/ThemeToggle";
import "./dashboard.css";

export default function DashboardPage() {
  const { user, logout, isLoading: authLoading, refreshAuthStatus } = useAuth();
  const router = useRouter();
  const {
    tasks,
    isLoading: tasksLoading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleTaskCompletion,
  } = useTasks(user?.id);

  const [showTaskForm, setShowTaskForm] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isRedirecting, setIsRedirecting] = useState(false);

  // Redirect to login if user is not authenticated
  useEffect(() => {
    // Only redirect if we're done loading AND user is not authenticated
    // We should not redirect while auth is still loading
    if (!authLoading && !user) {
      setIsRedirecting(true);
      router.replace("/login");
    }
    // Don't redirect while loading - this was likely causing the issue
  }, [user, authLoading, router]);

  // Additional effect to handle authentication state changes after initial load
  useEffect(() => {
    if (authLoading && !user) {
      // Still loading auth state, don't do anything yet
      return;
    }

    // If we've loaded auth state and user is now authenticated, ensure we stay on dashboard
    if (!authLoading && user && isRedirecting) {
      // Cancel redirection if user becomes authenticated
      setIsRedirecting(false);
    }
  }, [authLoading, user, isRedirecting]);

  // Listen for unauthorized events (e.g., 401 errors from API calls)
  useEffect(() => {
    const handleUnauthorized = () => {
      // Log out the user and redirect to login
      logout();
      setIsRedirecting(true);
      router.replace("/login");
    };

    // Listen for forbidden events (e.g., 403 errors from API calls)
    const handleForbidden = () => {
      // Log out the user and redirect to login
      logout();
      setIsRedirecting(true);
      router.replace("/login");
    };

    window.addEventListener('unauthorized', handleUnauthorized);
    window.addEventListener('forbidden', handleForbidden);

    return () => {
      window.removeEventListener('unauthorized', handleUnauthorized);
      window.removeEventListener('forbidden', handleForbidden);
    };
  }, [logout, router]);

  // Fetch tasks when user is authenticated
  useEffect(() => {
    if (!authLoading && user) {
      fetchTasks();
    }
  }, [user?.id, authLoading, fetchTasks]);

  const handleCreateTask = async (taskData: TaskCreateData) => {
    const result = await createTask(taskData);
    if (result && result.success) {
      // Task created successfully, don't redirect
      // Optionally close the form after successful creation
      // setShowTaskForm(false); // Uncomment if you want to close the form after successful creation
    }
    return result; // Return the result to the form
  };

  const handleUpdateTask = async (
    id: string,
    updatedData: Partial<TaskCreateData>
  ) => {
    await updateTask(id, updatedData);
  };

  const handleDeleteTask = async (id: string) => {
    await deleteTask(id);
  };

  const handleToggleTask = async (id: string, completed: boolean) => {
    await toggleTaskCompletion(id, completed);
  };

  const handleBulkComplete = async (taskIds: string[]) => {
    // Update all selected tasks to completed
    for (const taskId of taskIds) {
      await toggleTaskCompletion(taskId, true);
    }
  };

  // Generate initials from email
  const getInitials = (email: string) => {
    if (!email) return "U";

    const [username] = email.split("@");
    if (!username) return "U";

    const parts = username.split(".");
    if (parts.length > 1) {
      // For emails like john.doe@gmail.com -> JD
      return (parts[0][0] + parts[1][0]).toUpperCase();
    } else {
      // For emails like abdulqadir@gmail.com -> AQ (first two letters)
      return username.substring(0, 2).toUpperCase();
    }
  };

  // Generate background color based on email
  const getBackgroundColor = (email: string) => {
    if (!email) return "#6366F1"; // Default indigo

    let hash = 0;
    for (let i = 0; i < email.length; i++) {
      hash = email.charCodeAt(i) + ((hash << 5) - hash);
    }

    const colors = [
      "#6366F1", // indigo
      "#8B5CF6", // violet
      "#EC4899", // pink
      "#EF4444", // red
      "#F59E0B", // amber
      "#10B981", // emerald
      "#3B82F6", // blue
      "#F97316", // orange
    ];

    return colors[Math.abs(hash) % colors.length];
  };

  const handleLogout = () => {
    logout();
    setIsRedirecting(true);
    router.replace("/login");
  };

  const toggleDropdown = () => {
    setShowDropdown(!showDropdown);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const dropdown = document.getElementById("user-dropdown");
      const avatarButton = document.getElementById("avatar-button");

      if (
        dropdown &&
        avatarButton &&
        !dropdown.contains(event.target as Node) &&
        !avatarButton.contains(event.target as Node)
      ) {
        setShowDropdown(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Listen for refreshTasks event to update task list
  useEffect(() => {
    const handleRefreshTasks = () => {
      if (!authLoading && user) {
        fetchTasks();
      }
    };

    window.addEventListener('refreshTasks', handleRefreshTasks);

    return () => {
      window.removeEventListener('refreshTasks', handleRefreshTasks);
    };
  }, [authLoading, user, fetchTasks]);

  // Show loading state while checking auth status
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 dark:border-indigo-400"></div>
      </div>
    );
  }

  // If user is not authenticated and not loading, or if we're in the process of redirecting
  if ((!authLoading && !user) || (isRedirecting && !user)) {
    // Show a minimal loading state while redirect happens in useEffect
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-700 dark:text-gray-300">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  const initials = user ? getInitials(user.email) : "";
  const backgroundColor = user ? getBackgroundColor(user.email) : "#6366F1";

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Tasks Dashboard
          </h1>
          <div className="flex items-center space-x-4">
            <ThemeToggle />
            {user && !isRedirecting ? (
              <div className="user-avatar-container">
                <button
                  id="avatar-button"
                  className="flex items-center space-x-2"
                  onClick={toggleDropdown}
                >
                  <div className="user-avatar" style={{ backgroundColor }}>
                    {initials}
                  </div>
                </button>

                {showDropdown && (
                  <div
                    id="user-dropdown"
                    className={`dropdown ${showDropdown ? "show" : ""}`}
                  >
                    <div className="dropdown-item">{user.email}</div>
                    <div className="dropdown-divider"></div>
                    <button
                      className="dropdown-item"
                      onClick={() => router.push("/profile")}
                    >
                      Profile
                    </button>
                    <button className="dropdown-item" onClick={handleLogout}>
                      Logout
                    </button>
                  </div>
                )}
              </div>
            ) : !isRedirecting ? (
              <div className="flex space-x-2">
                <button
                  onClick={() => router.push("/login")}
                  className="text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300"
                >
                  Login
                </button>
                <span className="text-gray-400 dark:text-gray-500">|</span>
                <button
                  onClick={() => router.push("/signup")}
                  className="text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300"
                >
                  Sign Up
                </button>
              </div>
            ) : null}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {!user && !isRedirecting && (
          <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-md">
            <p className="text-blue-700 dark:text-blue-300">
              Please{" "}
              <button
                onClick={() => router.push("/login")}
                className="font-medium underline"
              >
                log in
              </button>{" "}
              to view and manage your tasks.
            </p>
          </div>
        )}

        {error && (
          <div className="rounded-md bg-red-50 dark:bg-red-900/20 p-4 mb-4">
            <div className="text-sm text-red-700 dark:text-red-300">
              {error !== 'User ID is required to fetch tasks' &&
                error !== 'User ID is required to create a task. Please log in again.'
                ? error : 'Loading...'}
            </div>
          </div>
        )}

        {/* Main content grid */}
        <div className="grid grid-cols-1 gap-6">
          {/* Task list and form */}
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                  My Tasks
                </h2>
                <div className="flex space-x-2">
                  {user && !isRedirecting && (
                    <button
                      onClick={fetchTasks}
                      className="inline-flex items-center rounded border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600"
                      title="Refresh tasks"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="-ml-0.5 mr-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      Refresh
                    </button>
                  )}
                  {user && !isRedirecting && (
                    <button
                      onClick={() => setShowTaskForm(!showTaskForm)}
                      className="inline-flex items-center rounded border border-transparent bg-green-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 dark:bg-green-500 dark:hover:bg-green-600"
                    >
                      {showTaskForm ? "Cancel" : "Add Task"}
                    </button>
                  )}
                </div>
              </div>

              {user && !isRedirecting && showTaskForm && (
                <div className="mb-8">
                  <TaskForm
                    onSubmit={handleCreateTask}
                    onCancel={() => setShowTaskForm(false)}
                  />
                </div>
              )}

              {(tasksLoading || authLoading || isRedirecting) ? (
                <div className="flex justify-center items-center py-12">
                  <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 dark:border-indigo-400"></div>
                </div>
              ) : (
                <NewTaskList
                  tasks={tasks}
                  onToggle={user ? handleToggleTask : () => { }}
                  onDelete={user ? handleDeleteTask : () => { }}
                  onEdit={user ? handleUpdateTask : () => { }}
                  onBulkComplete={user ? handleBulkComplete : () => { }}
                />
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
