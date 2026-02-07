/**
 * Safe storage utility for Next.js applications
 * This utility handles localStorage access safely during both client and server rendering
 */

export interface StorageType {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
  removeItem(key: string): void;
  clear(): void;
}

class SafeStorage implements StorageType {
  /**
   * Check if we're running in a browser environment
   */
  private isBrowser(): boolean {
    return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';
  }

  /**
   * Get an item from localStorage
   */
  getItem(key: string): string | null {
    if (!this.isBrowser()) {
      return null;
    }
    
    try {
      return window.localStorage.getItem(key);
    } catch (error) {
      console.warn(`Error reading from localStorage: ${error}`);
      return null;
    }
  }

  /**
   * Set an item in localStorage
   */
  setItem(key: string, value: string): void {
    if (!this.isBrowser()) {
      return;
    }
    
    try {
      window.localStorage.setItem(key, value);
    } catch (error) {
      console.warn(`Error writing to localStorage: ${error}`);
    }
  }

  /**
   * Remove an item from localStorage
   */
  removeItem(key: string): void {
    if (!this.isBrowser()) {
      return;
    }
    
    try {
      window.localStorage.removeItem(key);
    } catch (error) {
      console.warn(`Error removing from localStorage: ${error}`);
    }
  }

  /**
   * Clear all items from localStorage
   */
  clear(): void {
    if (!this.isBrowser()) {
      return;
    }
    
    try {
      window.localStorage.clear();
    } catch (error) {
      console.warn(`Error clearing localStorage: ${error}`);
    }
  }
}

// Create a singleton instance
export const safeStorage = new SafeStorage();

// Export individual helper functions for convenience
export const getStorageItem = (key: string): string | null => safeStorage.getItem(key);
export const setStorageItem = (key: string, value: string): void => safeStorage.setItem(key, value);
export const removeStorageItem = (key: string): void => safeStorage.removeItem(key);