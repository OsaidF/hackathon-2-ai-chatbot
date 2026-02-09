import { MAX_MESSAGE_LENGTH, MIN_MESSAGE_LENGTH } from './constants';

/**
 * Validation result interface
 */
export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * Validate message is not empty or whitespace-only
 */
export function validateMessageNotEmpty(message: string): ValidationResult {
  const trimmed = message.trim();

  if (trimmed.length === 0) {
    return {
      isValid: false,
      error: 'Message cannot be empty',
    };
  }

  return { isValid: true };
}

/**
 * Validate message length
 */
export function validateMessageLength(message: string): ValidationResult {
  if (message.length > MAX_MESSAGE_LENGTH) {
    return {
      isValid: false,
      error: `Message too long (maximum ${MAX_MESSAGE_LENGTH} characters)`,
    };
  }

  if (message.length < MIN_MESSAGE_LENGTH) {
    return {
      isValid: false,
      error: `Message too short (minimum ${MIN_MESSAGE_LENGTH} character)`,
    };
  }

  return { isValid: true };
}

/**
 * Validate message (all checks)
 */
export function validateMessage(message: string): ValidationResult {
  // Check not empty
  const notEmptyResult = validateMessageNotEmpty(message);
  if (!notEmptyResult.isValid) {
    return notEmptyResult;
  }

  // Check length
  const lengthResult = validateMessageLength(message);
  if (!lengthResult.isValid) {
    return lengthResult;
  }

  return { isValid: true };
}

/**
 * Check if message is valid (boolean)
 */
export function isValidMessage(message: string): boolean {
  return validateMessage(message).isValid;
}

/**
 * Get remaining character count
 */
export function getRemainingChars(message: string): number {
  return MAX_MESSAGE_LENGTH - message.length;
}
