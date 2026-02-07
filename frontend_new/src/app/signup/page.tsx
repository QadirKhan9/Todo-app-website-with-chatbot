// frontend/src/app/signup/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/components/AuthProvider';
import Link from 'next/link';
import ThemeToggle from '@/components/ThemeToggle';
import { validatePassword, getPasswordRequirements } from '@/utils/passwordValidation';
import { isErrorForField } from '@/utils/errorHandler';
import { parseAxiosError } from '@/lib/axiosErrorHandler';
import { Eye, EyeOff } from 'lucide-react';

export default function SignupPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [usernameError, setUsernameError] = useState('');
  const [isPasswordFocused, setIsPasswordFocused] = useState(false);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const router = useRouter();
  const { signup, isLoading, isAuthenticated } = useAuth();

  // Redirect to dashboard if user is already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, router]);

  // Track password validation in real-time
  const passwordValidation = validatePassword(password);

  // Determine if password is valid
  const isPasswordValid = passwordValidation.isValid;

  // Determine if passwords match
  const passwordsMatch = password === confirmPassword;

  // Determine if confirm password should be enabled
  const isConfirmPasswordEnabled = isPasswordValid;

  // Determine which requirements are met
  const requirements = getPasswordRequirements();
  const fulfilledRequirements = requirements.map(req =>
    passwordValidation.errors.indexOf(req) === -1
  );

  // Validate username
  const validateUsername = (username: string): string | null => {
    if (username.length < 3) {
      return 'Username must be at least 3 characters';
    }

    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
      return 'Username can only contain letters, numbers, and underscores';
    }

    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');
    setUsernameError('');
    setHasSubmitted(true);

    // Frontend validation for username
    const usernameValidationError = validateUsername(username);
    if (usernameValidationError) {
      setUsernameError(usernameValidationError);
      return;
    }

    // Frontend validation
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password against backend rules
    if (!passwordValidation.isValid) {
      // Error will be shown in the UI as per the new UX
      return;
    }

    try {
      const result = await signup(username, email, password);
      if (result.success) {
        // Show success message
        setSuccessMessage('Signup successful!');
        setError(''); // Clear any previous error

        // Redirect to login page after a short delay to show the success message
        setTimeout(() => {
          router.replace('/login');
        }, 1500);
      } else {
        // Check if it's a username conflict error
        if (result.error && result.error.toLowerCase().includes('username')) {
          setUsernameError(result.error);
        } else {
          setError(result.error || 'Signup failed');
          setSuccessMessage(''); // Clear any previous success message
        }
      }
    } catch (err: any) {
      // Use centralized error parsing for other errors
      const errorMessage = parseAxiosError(err);

      // Check if it's a username conflict error
      if (errorMessage && errorMessage.toLowerCase().includes('username')) {
        setUsernameError(errorMessage);
      } else {
        setError(errorMessage);
        setSuccessMessage(''); // Clear any previous success message
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="flex justify-end">
          <ThemeToggle />
        </div>
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
            Create your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {successMessage && (
            <div className="rounded-md bg-green-50 dark:bg-green-900/20 p-4">
              <div className="flex items-center">
                <svg className="h-5 w-5 text-green-400 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div className="text-sm text-green-700 dark:text-green-300">{successMessage}</div>
              </div>
            </div>
          )}
          {error && (
            <div className="rounded-md bg-red-50 dark:bg-red-900/20 p-4">
              <div className="text-sm text-red-700 dark:text-red-300">{error}</div>
            </div>
          )}
          <input type="hidden" name="remember" defaultValue="true" />
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="username" className="sr-only">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                disabled={isLoading}
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border ${
                  usernameError ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                } placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm`}
                placeholder="Username"
                value={username}
                onChange={(e) => {
                  setUsername(e.target.value);
                  // Clear username error when user starts typing
                  if (usernameError) {
                    setUsernameError('');
                  }
                  // Clear general error when user starts typing
                  if (error) {
                    setError('');
                  }
                }}
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                This will be visible to others
              </p>
              {usernameError && (
                <div className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {usernameError}
                </div>
              )}
            </div>
            <div>
              <label htmlFor="email-address" className="sr-only">
                Email address
              </label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                disabled={isLoading}
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border ${
                  error && isErrorForField({ status: 0, message: error }, 'email') ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                } placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm`}
                placeholder="Email address"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  // Clear email-specific error when user starts typing
                  if (error && isErrorForField({ status: 0, message: error }, 'email')) {
                    setError('');
                  }
                }}
              />
              {error && isErrorForField({ status: 0, message: error }, 'email') && (
                <div className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {error}
                </div>
              )}
            </div>
            <div className="relative">
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                required
                disabled={isLoading}
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border ${
                  (error && isErrorForField({ status: 0, message: error }, 'password')) || (!isPasswordValid && hasSubmitted) ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                } placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm pr-10`}
                placeholder="Password"
                value={password}
                onFocus={() => setIsPasswordFocused(true)}
                onBlur={() => setIsPasswordFocused(false)}
                onChange={(e) => {
                  setPassword(e.target.value);
                  // Clear password-specific error when user starts typing
                  if (error && isErrorForField({ status: 0, message: error }, 'password')) {
                    setError('');
                  }
                }}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <EyeOff size={20} />
                ) : (
                  <Eye size={20} />
                )}
              </button>

              {/* Password helper section - appears on focus */}
              {(isPasswordFocused || hasSubmitted) && (
                <div className="mt-3 transition-opacity duration-300 ease-in-out">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Create a strong password</p>

                  {hasSubmitted && !isPasswordValid && (
                    <p className="text-xs text-yellow-600 dark:text-yellow-400 mb-2">
                      Almost there! Just fix the highlighted items.
                    </p>
                  )}

                  <ul className="text-sm">
                    {requirements.map((req, index) => {
                      // Simplify the requirement text for display
                      let displayText = req;
                      if (req.includes('8 characters')) displayText = 'At least 8 characters';
                      if (req.includes('uppercase letter')) displayText = 'At least 1 uppercase letter';
                      if (req.includes('lowercase letter')) displayText = 'At least 1 lowercase letter';
                      if (req.includes('digit')) displayText = 'At least 1 digit';
                      if (req.includes('special character')) displayText = 'At least 1 special character';

                      const isFulfilled = fulfilledRequirements[index];

                      // Determine color and icon based on state
                      let textColor = 'text-gray-400'; // Default grey
                      let icon = '';

                      if (hasSubmitted && !isPasswordValid && !isFulfilled) {
                        // Show red for unmet requirements after submission
                        textColor = 'text-red-500';
                        icon = '✗ ';
                      } else if (isFulfilled) {
                        // Show green for fulfilled requirements
                        textColor = 'text-green-500';
                        icon = '✓ ';
                      }

                      return (
                        <li
                          key={index}
                          className={`flex items-center ${textColor} mt-1`}
                        >
                          <span className="mr-2">{icon}</span>
                          <span>{displayText}</span>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              )}

              {error && isErrorForField({ status: 0, message: error }, 'password') && (
                <div className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {error}
                </div>
              )}
            </div>
            <div className="relative">
              <label htmlFor="confirm-password" className="sr-only">
                Confirm Password
              </label>
              <input
                id="confirm-password"
                name="confirm-password"
                type={showConfirmPassword ? "text" : "password"}
                autoComplete="new-password"
                required
                disabled={isLoading || !isConfirmPasswordEnabled}
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border ${
                  error && (isErrorForField({ status: 0, message: error }, 'password') || isErrorForField({ status: 0, message: error }, 'confirm')) ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                } placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm ${
                  !isConfirmPasswordEnabled ? 'opacity-50 cursor-not-allowed' : ''
                } pr-10`}
                placeholder={isConfirmPasswordEnabled ? "Confirm Password" : "Password must be valid first"}
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  // Clear password-specific error when user starts typing
                  if (error && (isErrorForField({ status: 0, message: error }, 'password') || isErrorForField({ status: 0, message: error }, 'confirm'))) {
                    setError('');
                  }
                }}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                aria-label={showConfirmPassword ? "Hide confirm password" : "Show confirm password"}
                disabled={!isConfirmPasswordEnabled}
              >
                {showConfirmPassword ? (
                  <EyeOff size={20} />
                ) : (
                  <Eye size={20} />
                )}
              </button>
              {!passwordsMatch && confirmPassword && (
                <div className="mt-1 text-sm text-red-600 dark:text-red-400">
                  Passwords don't match yet
                </div>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className={`group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md ${
                isLoading
                  ? 'bg-indigo-400 dark:bg-indigo-500'
                  : 'bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600'
              } text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:focus:ring-offset-gray-900`}
            >
              {isLoading ? 'Signing up...' : 'Sign up'}
            </button>
          </div>

          <div className="text-sm text-center">
            <Link href="/login" className="font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300">
              Already have an account? Sign in here
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}