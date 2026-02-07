// frontend/src/lib/axiosLoginErrorHandler.ts

/**
 * Safely extracts error message from Axios error response for login
 * @param error The error object from Axios
 * @returns User-friendly error message
 */
export const parseLoginAxiosError = (error: any): string => {
  // Check if it's a network error (no response)
  if (!error.response) {
    return 'Unable to connect to server';
  }

  const status = error.response.status;
  const detail = error.response.data?.detail;

  switch (status) {
    case 401:
      return 'Invalid email or password';
    
    case 403:
      return 'Account is inactive or not verified';
    
    case 422:
      // Handle validation errors
      if (Array.isArray(detail)) {
        return detail.map((item: any) => item.msg).join(', ');
      } else if (typeof detail === 'string') {
        return detail;
      } else {
        return 'Validation error occurred';
      }
    
    case 500:
      // For 500 errors, always return a generic message to avoid exposing backend details
      return 'Server error occurred. Please try again later.';
    
    default:
      // For other errors, try to get the message from response data
      return error.response.data?.message || 
             error.message || 
             'An error occurred during login.';
  }
};