// frontend/src/utils/errorHandler.ts

/**
 * Parses API error responses and returns user-friendly messages
 * @param error The error object from Axios
 * @returns Object containing status code and user-friendly message
 */
export const parseApiError = (error: any) => {
  const status = error.response?.status;
  const detail = error.response?.data?.detail;

  // Prevent exposing backend stack traces
  if (status === 500) {
    // For 500 errors, always return a generic message regardless of what the server sends
    return {
      status,
      message: 'Server error occurred. Please try again later.'
    };
  }

  switch (status) {
    case 422:
      // Handle validation errors
      if (Array.isArray(detail)) {
        return {
          status,
          message: detail.map((item: any) => item.msg).join(', ')
        };
      } else if (typeof detail === 'string') {
        return {
          status,
          message: detail
        };
      } else {
        return {
          status,
          message: 'Validation error occurred'
        };
      }

    case 409:
      // Handle conflict (email already exists)
      return {
        status,
        message: 'Email already exists. Please login or use another email.'
      };

    default:
      // Handle other errors
      return {
        status,
        message: error.response?.data?.message || error.message || 'An error occurred during signup.'
      };
  }
};

/**
 * Determines if an error should be displayed as a field-specific error
 * @param error The parsed error object
 * @param field The field name to check against
 * @returns Boolean indicating if the error applies to the field
 */
export const isErrorForField = (error: { status: number; message: string }, field: string): boolean => {
  if (!error || !error.message) return false;
  
  const lowerMessage = error.message.toLowerCase();
  const lowerField = field.toLowerCase();
  
  // Map field names to keywords in error messages
  const fieldKeywords: Record<string, string[]> = {
    email: ['email', 'address'],
    password: ['password', 'character', 'uppercase', 'lowercase', 'digit', 'special'],
    confirmPassword: ['confirm', 'match']
  };
  
  if (fieldKeywords[lowerField]) {
    return fieldKeywords[lowerField].some(keyword => lowerMessage.includes(keyword));
  }
  
  return lowerMessage.includes(lowerField);
};