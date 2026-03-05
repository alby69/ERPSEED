/**
 * Data Binding Engine
 *
 * Evaluates expressions within {{ }} using a provided context.
 */

const BUILT_IN_FUNCS = {
  UPPER: (val) => String(val).toUpperCase(),
  LOWER: (val) => String(val).toLowerCase(),
  IF: (cond, then, otherwise) => (cond ? then : otherwise),
  COUNT: (arr) => (Array.isArray(arr) ? arr.length : 0),
  SUM: (arr, field) => {
    if (!Array.isArray(arr)) return 0;
    return arr.reduce((acc, item) => {
      const val = field ? item[field] : item;
      return acc + (Number(val) || 0);
    }, 0);
  },
  NOW: () => new Date().toISOString(),
  FORMAT_CURRENCY: (val, symbol = '€') => {
    return `${symbol} ${Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }
};

/**
 * Evaluates a single expression string.
 * @param {string} expression - The expression to evaluate (e.g., "user.name")
 * @param {Object} context - The data context
 * @returns {any} - The evaluated value
 */
export const evaluateExpression = (expression, context = {}) => {
  const fullContext = { ...BUILT_IN_FUNCS, ...context };
  try {
    const keys = Object.keys(fullContext);
    const values = Object.values(fullContext);
    // eslint-disable-next-line no-new-func
    const fn = new Function(...keys, `try { return ${expression}; } catch(e) { return undefined; }`);
    return fn(...values);
  } catch (error) {
    console.warn(`Error creating evaluator for expression: ${expression}`, error);
    return undefined;
  }
};

/**
 * Replaces all occurrences of {{expression}} in a string.
 * @param {string} template - The string containing expressions
 * @param {Object} context - The data context
 * @returns {string} - The interpolated string
 */
export const interpolate = (template, context = {}) => {
  if (typeof template !== 'string') return template;

  return template.replace(/\{\{(.+?)\}\}/g, (match, expression) => {
    const value = evaluateExpression(expression, context);
    return value !== undefined && value !== null ? String(value) : '';
  });
};

/**
 * Recursively interpolates expressions in an object or array.
 * @param {any} data - Object or array to process
 * @param {Object} context - The data context
 * @returns {any} - Processed data
 */
export const resolveDataBinding = (data, context = {}) => {
  if (typeof data === 'string') {
    // If the whole string is just one expression, return the raw value (not just stringified)
    const match = data.match(/^\{\{(.+?)\}\}$/);
    if (match) {
      return evaluateExpression(match[1], context);
    }
    return interpolate(data, context);
  }

  if (Array.isArray(data)) {
    return data.map(item => resolveDataBinding(item, context));
  }

  if (data !== null && typeof data === 'object') {
    const resolved = {};
    for (const [key, value] of Object.entries(data)) {
      resolved[key] = resolveDataBinding(value, context);
    }
    return resolved;
  }

  return data;
};

export default {
  evaluateExpression,
  interpolate,
  resolveDataBinding
};
