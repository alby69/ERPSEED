import { evaluateExpression, interpolate, resolveDataBinding } from '../utils/binding';
import { describe, it, expect } from 'vitest';

describe('Data Binding Engine', () => {
  const context = {
    user: {
      name: 'John Doe',
      age: 30
    },
    items: [
      { id: 1, price: 10 },
      { id: 2, price: 20 }
    ],
    status: 'pending'
  };

  describe('evaluateExpression', () => {
    it('should evaluate simple paths', () => {
      expect(evaluateExpression('user.name', context)).toBe('John Doe');
      expect(evaluateExpression('user.age', context)).toBe(30);
    });

    it('should evaluate built-in functions', () => {
      expect(evaluateExpression('UPPER(user.name)', context)).toBe('JOHN DOE');
      expect(evaluateExpression('COUNT(items)', context)).toBe(2);
      expect(evaluateExpression('SUM(items, "price")', context)).toBe(30);
      expect(evaluateExpression('IF(status === "pending", "Wait", "Go")', context)).toBe('Wait');
    });

    it('should return undefined for invalid paths', () => {
      expect(evaluateExpression('nonexistent.path', context)).toBeUndefined();
    });
  });

  describe('interpolate', () => {
    it('should interpolate strings with expressions', () => {
      expect(interpolate('Hello {{user.name}}!', context)).toBe('Hello John Doe!');
      expect(interpolate('Age: {{user.age}}, Status: {{UPPER(status)}}', context)).toBe('Age: 30, Status: PENDING');
    });

    it('should handle missing values gracefully', () => {
      expect(interpolate('Value: {{missing}}', context)).toBe('Value: ');
    });
  });

  describe('resolveDataBinding', () => {
    it('should resolve expressions in objects', () => {
      const input = {
        title: 'User: {{user.name}}',
        details: {
          age: '{{user.age}}',
          active: true
        }
      };
      const expected = {
        title: 'User: John Doe',
        details: {
          age: 30, // Note: preserved as number because it was the whole string
          active: true
        }
      };
      expect(resolveDataBinding(input, context)).toEqual(expected);
    });

    it('should resolve expressions in arrays', () => {
      const input = ['{{user.name}}', '{{COUNT(items)}}'];
      const expected = ['John Doe', 2];
      expect(resolveDataBinding(input, context)).toEqual(expected);
    });
  });
});
