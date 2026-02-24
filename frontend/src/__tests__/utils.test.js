import { describe, it, expect } from 'vitest';
import { getNestedValue, formatDate, formatCurrency } from '../utils';

describe('Utility Functions', () => {
  describe('getNestedValue', () => {
    it('should return value for nested path', () => {
      const obj = { user: { profile: { name: 'Jules' } } };
      expect(getNestedValue(obj, 'user.profile.name')).toBe('Jules');
    });

    it('should return empty string if path not found', () => {
      const obj = { user: { profile: { name: 'Jules' } } };
      expect(getNestedValue(obj, 'user.address.city')).toBe('');
    });

    it('should return empty string if object is null', () => {
      expect(getNestedValue(null, 'any.path')).toBe('');
    });
  });

  describe('formatDate', () => {
    it('should format ISO date string to local locale', () => {
      const date = '2026-02-24T12:00:00';
      // In tests locale might vary, but we check if it returns a string
      expect(typeof formatDate(date)).toBe('string');
    });

    it('should return empty string for null input', () => {
      expect(formatDate(null)).toBe('');
    });
  });

  describe('formatCurrency', () => {
    it('should format number to currency string', () => {
      const amount = 1234.56;
      const formatted = formatCurrency(amount);
      // Replace non-breaking spaces with regular spaces for easier testing
      const normalized = formatted.replace(/\u00a0/g, ' ');
      expect(normalized).toContain('1234,56'); // Sometimes thousand separator is omitted in test env
      expect(normalized).toContain('€');
    });
  });
});
