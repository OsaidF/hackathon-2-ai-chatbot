/**
 * Custom API Error class
 */
export class ApiError extends Error {
  public status: number;
  public code: string;
  public detail?: string;

  constructor(status: number, error: { error: string; code: string; detail?: string }) {
    super(error.error);
    this.name = 'ApiError';
    this.status = status;
    this.code = error.code;
    this.detail = error.detail;
  }

  /**
   * Check if error is a network error
   */
  isNetworkError(): boolean {
    return this.status === 0 || this.code === 'NETWORK_ERROR';
  }

  /**
   * Check if error is an authentication error
   */
  isAuthError(): boolean {
    return this.status === 401 || this.status === 403;
  }

  /**
   * Check if error is a validation error
   */
  isValidationError(): boolean {
    return this.status === 400;
  }

  /**
   * Check if error is a server error
   */
  isServerError(): boolean {
    return this.status >= 500;
  }

  /**
   * Get user-friendly error message
   */
  getUserMessage(): string {
    if (this.isNetworkError()) {
      return 'Network error. Please check your connection.';
    }
    if (this.isAuthError()) {
      return 'Session expired. Please log in again.';
    }
    if (this.isValidationError()) {
      return this.detail || this.message;
    }
    if (this.isServerError()) {
      return 'Server error. Please try again later.';
    }
    return this.message;
  }
}
