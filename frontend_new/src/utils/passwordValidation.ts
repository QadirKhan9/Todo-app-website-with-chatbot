// frontend/src/utils/passwordValidation.ts

/**
 * Validates password against backend requirements:
 * - Min 8 characters
 * - At least 1 uppercase letter
 * - At least 1 lowercase letter
 * - At least 1 digit
 * - At least 1 special character
 */
export const validatePassword = (password: string): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];

  // Check minimum length
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters');
  }

  // Check for uppercase letter
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least 1 uppercase letter');
  }

  // Check for lowercase letter
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least 1 lowercase letter');
  }

  // Check for digit
  if (!/\d/.test(password)) {
    errors.push('Password must contain at least 1 digit');
  }

  // Check for special character
  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    errors.push('Password must contain at least 1 special character');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Checks if password meets all requirements without returning error messages
 */
export const isPasswordValid = (password: string): boolean => {
  return validatePassword(password).isValid;
};

/**
 * Returns the list of password requirements as a static array
 */
export const getPasswordRequirements = (): string[] => [
  'Password must be at least 8 characters',
  'Password must contain at least 1 uppercase letter',
  'Password must contain at least 1 lowercase letter',
  'Password must contain at least 1 digit',
  'Password must contain at least 1 special character'
];