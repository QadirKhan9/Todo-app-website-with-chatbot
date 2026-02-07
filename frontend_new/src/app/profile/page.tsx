'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/components/AuthProvider';
import { useTasks } from '@/hooks/useTasks';
import ThemeToggle from '@/components/ThemeToggle';
import { User } from '@/lib/types';

export default function ProfilePage() {
  const router = useRouter();
  const { user, isLoading, refreshAuthStatus } = useAuth();
  const [profile, setProfile] = useState<User | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
  });
  const [message, setMessage] = useState('');

  // Initialize tasks state separately to handle loading properly
  const [tasks, setTasks] = useState<any[]>([]);
  const [tasksLoading, setTasksLoading] = useState(true);

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || user.email?.split('@')[0] || '',
        email: user.email || '',
      });

      // Fetch user profile details including account creation date
      const fetchUserProfile = async () => {
        try {
          // Import the apiClient to fetch user profile
          const { apiClient } = await import('@/lib/api');

          // Try to fetch user profile from the backend
          try {
            const response = await apiClient.client.get('/users/me');

            // Handle different possible response structures for user profile
            let userProfile = { ...user }; // Start with existing user data

            if (response.data && typeof response.data === 'object') {
              const responseData = response.data as { data?: { user?: any }, user?: any };

              if (responseData.data && responseData.data.user) {
                // Standard API response structure
                userProfile = { ...userProfile, ...responseData.data.user };
              } else if (responseData.user) {
                // Alternative structure
                userProfile = { ...userProfile, ...responseData.user };
              } else {
                // Direct user object
                userProfile = { ...userProfile, ...response.data };
              }
            }

            setProfile(userProfile);
          } catch (profileError) {
            // If fetching profile fails, use the user data from auth state
            // but try to enhance it with creation date from JWT if available
            setProfile(user);
            console.warn('Could not fetch detailed user profile:', profileError);
          }

          // Fetch tasks for the user
          const { todoService } = await import('@/services/todoService');
          const tasksResponse = await todoService.getTasks();

          // Handle different possible response structures
          let tasksData = [];
          if (tasksResponse.data && typeof tasksResponse.data === 'object') {
            const taskData = tasksResponse.data as { data?: { tasks?: any[] }, tasks?: any[] };

            if (taskData.data && Array.isArray(taskData.data.tasks)) {
              tasksData = taskData.data.tasks;
            } else if (Array.isArray(taskData.tasks)) {
              tasksData = taskData.tasks;
            } else if (Array.isArray(taskData.data)) {
              tasksData = taskData.data;
            } else if (Array.isArray(tasksResponse.data)) {
              tasksData = tasksResponse.data;
            } else {
              console.warn('Unexpected response structure for getTasks:', tasksResponse.data);
              tasksData = [];
            }
          }

          setTasks(tasksData);
        } catch (error) {
          console.error('Error fetching user profile or tasks:', error);
          // Set profile with available user data
          setProfile(user);
          setTasks([]);
        } finally {
          setTasksLoading(false);
        }
      };

      fetchUserProfile();
    }
  }, [user]);

  const handleEditToggle = () => {
    setIsEditing(!isEditing);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      // In a real application, you would make an API call to update the profile
      // For now, we'll just simulate the update

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));

      // Update the profile state
      if (profile) {
        const updatedProfile = {
          ...profile,
          username: formData.username,
          email: formData.email,
        };

        setProfile(updatedProfile);
        setIsEditing(false);
        setMessage('Profile updated successfully!');

        // Refresh auth status to reflect changes
        await refreshAuthStatus();

        // Clear message after 3 seconds
        setTimeout(() => setMessage(''), 3000);
      }
    } catch (error) {
      setMessage('Failed to update profile. Please try again.');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 dark:border-indigo-400"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-700 dark:text-gray-300">Please log in to view your profile.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
          <div className="flex items-center">
            <button
              onClick={() => router.back()}
              className="mr-4 inline-flex items-center rounded border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium leading-4 text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
            >
              <svg
                className="-ml-0.5 mr-2 h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back
            </button>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Profile
            </h1>
          </div>
          <ThemeToggle />
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {message && (
          <div className="mb-6 p-4 rounded-md bg-green-50 dark:bg-green-900/20">
            <div className="text-sm text-green-700 dark:text-green-300">
              {message}
            </div>
          </div>
        )}

        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white">
              User Information
            </h2>
            <button
              onClick={handleEditToggle}
              className="inline-flex items-center rounded border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:bg-indigo-500 dark:hover:bg-indigo-600"
            >
              {isEditing ? 'Cancel' : 'Edit Profile'}
            </button>
          </div>

          {isEditing ? (
            <form onSubmit={handleSubmit}>
              <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <div className="sm:col-span-4">
                  <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Username
                  </label>
                  <input
                    type="text"
                    name="username"
                    id="username"
                    value={formData.username}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white sm:text-sm"
                  />
                </div>

                <div className="sm:col-span-4">
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Email address
                  </label>
                  <input
                    type="email"
                    name="email"
                    id="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white sm:text-sm"
                  />
                </div>
              </div>

              <div className="mt-8 flex justify-end">
                <button
                  type="submit"
                  className="inline-flex items-center rounded border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:bg-indigo-500 dark:hover:bg-indigo-600"
                >
                  Save Changes
                </button>
              </div>
            </form>
          ) : (
            <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
              <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <div className="sm:col-span-4">
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Username</dt>
                  <dd className="mt-1 text-sm text-gray-900 dark:text-gray-200">
                    {profile?.username || profile?.email?.split('@')[0] || 'Not provided'}
                  </dd>
                </div>

                <div className="sm:col-span-4">
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Email address</dt>
                  <dd className="mt-1 text-sm text-gray-900 dark:text-gray-200">
                    {profile?.email || 'Not provided'}
                  </dd>
                </div>

                <div className="sm:col-span-4">
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Total tasks</dt>
                  <dd className="mt-1 text-sm text-gray-900 dark:text-gray-200">
                    {tasksLoading ? 'Loading...' : tasks.length}
                  </dd>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}