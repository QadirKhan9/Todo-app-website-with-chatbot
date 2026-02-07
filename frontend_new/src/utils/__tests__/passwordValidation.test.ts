// frontend/src/utils/__tests__/passwordValidation.test.ts

import { validatePassword, isPasswordValid } from '../passwordValidation';

describe('Password Validation Utility', () => {
  test('should validate strong passwords correctly', () => {
    const strongPassword = 'MyStr0ng!Pass';
    expect(isPasswordValid(strongPassword)).toBe(true);
    expect(validatePassword(strongPassword).isValid).toBe(true);
    expect(validatePassword(strongPassword).errors).toHaveLength(0);
  });

  test('should reject passwords shorter than 8 characters', () => {
    const shortPassword = 'Abc1!';
    const result = validatePassword(shortPassword);
    
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Password must be at least 8 characters');
  });

  test('should reject passwords without uppercase letters', () => {
    const noUpperPassword = 'mystr0ng!pass';
    const result = validatePassword(noUpperPassword);
    
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Password must contain at least 1 uppercase letter');
  });

  test('should reject passwords without lowercase letters', () => {
    const noLowerPassword = 'MYSTR0NG!PASS';
    const result = validatePassword(noLowerPassword);
    
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Password must contain at least 1 lowercase letter');
  });

  test('should reject passwords without digits', () => {
    const noDigitPassword = 'MyStrong!Password';
    const result = validatePassword(noDigitPassword);
    
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Password must contain at least 1 digit');
  });

  test('should reject passwords without special characters', () => {
    const noSpecialPassword = 'MyStr0ngPassword';
    const result = validatePassword(noSpecialPassword);
    
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Password must contain at least 1 special character');
  });

  test('should accept all valid combinations', () => {
    const validPasswords = [
      'ValidPass1!',
      'Another2@Valid',
      'Test3#Password',
      'MyP4ss!Word',
      'ComplexP@ssw0rd99'
    ];

    validPasswords.forEach(password => {
      expect(isPasswordValid(password)).toBe(true);
      expect(validatePassword(password).isValid).toBe(true);
    });
  });
});