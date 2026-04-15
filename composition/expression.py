"""
Expression Engine - Valutazione espressioni dinamiche.

Permette di valutare espressioni Python in modo sicuro per
formule e logica di business dinamica.
"""
import ast
import operator
import re
from typing import Any, Dict, Callable, Optional
from functools import partial
import logging

logger = logging.getLogger(__name__)


class ExpressionEngine:
    """
    Motore per valutare espressioni dinamiche.

    Usage:
        engine = ExpressionEngine()
        result = engine.evaluate("quantity * price * (1 - discount)",
                                {'quantity': 10, 'price': 100, 'discount': 0.2})
        # result = 800
    """

    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.Is: operator.is_,
        ast.IsNot: operator.is_not,
        ast.In: operator.contains,
        ast.NotIn: lambda a, b: not operator.contains(b, a),
        ast.And: lambda a, b: a and b,
        ast.Or: lambda a, b: a or b,
        ast.Not: operator.not_,
        ast.UAdd: lambda x: +x,
        ast.USub: lambda x: -x,
    }

    def __init__(self, allowed_functions: Optional[Dict[str, Callable]] = None):
        self.context: Dict[str, Any] = {}
        self.allowed_functions = allowed_functions or {}
        self._register_builtin_functions()

    def _register_builtin_functions(self):
        """Registra funzioni built-in"""
        self.allowed_functions.update({
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'round': round,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'sorted': sorted,
            'reversed': reversed,
            'any': any,
            'all': all,
            'isinstance': isinstance,
            'type': type,
        })

    def set_context(self, **kwargs):
        """Imposta variabili nel contesto"""
        self.context.update(kwargs)

    def clear_context(self):
        """Pulisce il contesto"""
        self.context.clear()

    def evaluate(self, expression: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Valuta un'espressione.

        Args:
            expression: Stringa con l'espressione (es: "price * quantity")
            context: Dizionario con le variabili disponibili

        Returns:
            Risultato dell'espressione
        """
        ctx = {**self.context, **(context or {})}

        try:
            tree = ast.parse(expression, mode='eval')
            return self._eval_node(tree.body, ctx)
        except SyntaxError as e:
            raise ValueError(f"Syntax error in expression: {expression}") from e
        except Exception as e:
            raise RuntimeError(f"Error evaluating expression '{expression}': {e}") from e

    def _eval_node(self, node: ast.AST, context: Dict[str, Any]) -> Any:
        """Valuta un nodo AST"""

        if isinstance(node, ast.Constant):
            return node.value

        elif isinstance(node, ast.Name):
            if node.id in context:
                return context[node.id]
            raise NameError(f"Unknown variable: {node.id}")

        elif isinstance(node, ast.NameConstant):
            return node.value

        elif isinstance(node, ast.Num):
            return node.n

        elif isinstance(node, ast.Str):
            return node.s

        elif isinstance(node, ast.Attribute):
            obj = self._eval_node(node.value, context)
            return getattr(obj, node.attr)

        elif isinstance(node, ast.Subscript):
            value = self._eval_node(node.value, context)
            key = self._eval_node(node.slice, context)
            return value[key]

        elif isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else None

            if func_name in self.allowed_functions:
                func = self.allowed_functions[func_name]
                args = [self._eval_node(arg, context) for arg in node.args]
                kwargs = {kw.arg: self._eval_node(kw.value, context) for kw in node.keywords}
                return func(*args, **kwargs)

            elif func_name in context and callable(context[func_name]):
                func = context[func_name]
                args = [self._eval_node(arg, context) for arg in node.args]
                return func(*args)

            raise NameError(f"Unknown function: {func_name}")

        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, context)
            right = self._eval_node(node.right, context)
            op = self.SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise NotImplementedError(f"Operator {type(node.op)} not supported")
            return op(left, right)

        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, context)
            op = self.SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise NotImplementedError(f"Unary operator {type(node.op)} not supported")
            return op(operand)

        elif isinstance(node, ast.Compare):
            left = self._eval_node(node.left, context)
            ops = [self.SAFE_OPERATORS.get(type(op)) for op in node.ops]
            comparators = [self._eval_node(c, context) for c in node.comparators]

            result = True
            for op, comparator in zip(ops, [left] + comparators):
                if op is None:
                    raise NotImplementedError(f"Compare operator not supported")
                if not op(left, comparator):
                    result = False
                    break
                left = comparator
            return result

        elif isinstance(node, ast.BoolOp):
            values = [self._eval_node(v, context) for v in node.values]
            op = self.SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise NotImplementedError(f"Bool operator {type(node.op)} not supported")
            return op(*values)

        elif isinstance(node, ast.IfExp):
            test = self._eval_node(node.test, context)
            return self._eval_node(node.body if test else node.orelse, context)

        elif isinstance(node, ast.List):
            return [self._eval_node(elt, context) for elt in node.elts]

        elif isinstance(node, ast.Dict):
            return {
                self._eval_node(k, context): self._eval_node(v, context)
                for k, v in zip(node.keys, node.values)
            }

        elif isinstance(node, ast.Tuple):
            return tuple(self._eval_node(elt, context) for elt in node.elts)

        else:
            raise NotImplementedError(f"Unsupported AST node: {type(node).__name__}")

    def validate(self, expression: str) -> tuple[bool, Optional[str]]:
        """
        Valida un'espressione senza eseguirla.

        Returns:
            (is_valid, error_message)
        """
        try:
            tree = ast.parse(expression, mode='eval')
            self._check_node(tree.body)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, str(e)

    def _check_node(self, node: ast.AST):
        """Verifica che il nodo sia sicuro"""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id not in self.allowed_functions:
                        raise ValueError(f"Function not allowed: {child.func.id}")
                elif isinstance(child.func, ast.Attribute):
                    pass
            elif isinstance(child, ast.Import) or isinstance(child, ast.ImportFrom):
                raise ValueError("Import statements not allowed")


class Formula:
    """
    Rappresenta una formula con espressione e contesto.
    """

    def __init__(self, name: str, expression: str,
                 dependencies: Optional[list] = None,
                 description: str = ""):
        self.name = name
        self.expression = expression
        self.dependencies = dependencies or []
        self.description = description
        self.engine = ExpressionEngine()

    def compute(self, **context) -> Any:
        """Calcola il valore della formula"""
        return self.engine.evaluate(self.expression, context)

    def __repr__(self):
        return f"<Formula {self.name}={self.expression}>"


class FormulaRegistry:
    """Registro delle formule definite nel sistema."""

    _formulas: Dict[str, Formula] = {}

    @classmethod
    def register(cls, formula: Formula):
        cls._formulas[formula.name] = formula

    @classmethod
    def get(cls, name: str) -> Optional[Formula]:
        return cls._formulas.get(name)

    @classmethod
    def unregister(cls, name: str):
        cls._formulas.pop(name, None)

    @classmethod
    def list_all(cls) -> Dict[str, Formula]:
        return cls._formulas.copy()

    @classmethod
    def clear(cls):
        cls._formulas.clear()


def formula(name: str, expression: str, dependencies: Optional[list] = None):
    """Decorator per registrare una formula"""
    def decorator(func: Callable) -> Callable:
        f = Formula(name, expression, dependencies)
        FormulaRegistry.register(f)
        return func
    return decorator
