'use client';

import { useEffect } from 'react';

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        // Log the error to an error reporting service
        console.error('Next.js Root Error:', error);
    }, [error]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
            <div className="max-w-md w-full bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md text-center">
                <h2 className="text-2xl font-bold text-red-600 dark:text-red-400 mb-4">
                    Something went wrong!
                </h2>
                <p className="text-gray-600 dark:text-gray-300 mb-6">
                    {error.message || 'An unexpected error occurred.'}
                </p>
                <div className="flex flex-col gap-4">
                    <button
                        onClick={() => reset()}
                        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded transition-colors"
                    >
                        Try again
                    </button>
                    <button
                        onClick={() => window.location.reload()}
                        className="w-full bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 font-medium py-2 px-4 rounded transition-colors"
                    >
                        Refresh Page
                    </button>
                </div>
            </div>
        </div>
    );
}
