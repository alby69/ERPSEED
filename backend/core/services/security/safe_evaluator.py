import ast
import operator
import math

class SafeEvaluator:
    """
    A safe evaluator for mathematical and logical expressions.
    Replaces unsafe eval() for dynamic formulas.
    """

    # Supported operators
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.BitXor: operator.xor,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.And: operator.and_,
        ast.Or: operator.or_,
        ast.Not: operator.not_
    }

    # Supported functions (safe whitelist)
    safe_functions = {
        'abs': abs,
        'round': round,
        'max': max,
        'min': min,
        'sum': sum,
        'int': int,
        'float': float,
        'str': str,
        'len': len,
    }

    # Allowed math functions
    math_functions = {name: getattr(math, name) for name in dir(math) if not name.startswith('_')}

    @classmethod
    def evaluate(cls, expression, context=None):
        """
        Evaluate an expression safely.
        """
        if not expression:
            return None

        context = context or {}
        try:
            # Add safe functions to context
            eval_context = context.copy()
            eval_context.update(cls.safe_functions)
            eval_context.update(cls.math_functions)

            node = ast.parse(expression, mode='eval').body
            return cls._eval(node, eval_context)
        except Exception as e:
            # Log error in production
            return None

    @classmethod
    def _eval(cls, node, context):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return cls.operators[type(node.op)](cls._eval(node.left, context), cls._eval(node.right, context))
        elif isinstance(node, ast.UnaryOp):
            return cls.operators[type(node.op)](cls._eval(node.operand, context))
        elif isinstance(node, ast.Compare):
            left = cls._eval(node.left, context)
            for op, right in zip(node.ops, node.comparators):
                if not cls.operators[type(op)](left, cls._eval(right, context)):
                    return False
                left = cls._eval(right, context)
            return True
        elif isinstance(node, ast.BoolOp):
            values = [cls._eval(v, context) for v in node.values]
            if isinstance(node.op, ast.And):
                return all(values)
            elif isinstance(node.op, ast.Or):
                return any(values)
            return False
        elif isinstance(node, ast.Name):
            if node.id in context:
                return context[node.id]
            raise NameError(f"Name {node.id} is not defined or not allowed")
        elif isinstance(node, ast.Call):
            func = cls._eval(node.func, context)
            if not callable(func):
                raise TypeError(f"Object is not callable")
            # Check if it's a safe function
            if func not in cls.safe_functions.values() and func not in cls.math_functions.values():
                 raise ValueError(f"Function call not allowed")
            args = [cls._eval(arg, context) for arg in node.args]
            return func(*args)
        else:
            raise TypeError(f"Unsupported node type: {type(node)}")
