import pytest
from backend.core.services.security.safe_evaluator import SafeEvaluator

def test_safe_evaluator_basic_math():
    assert SafeEvaluator.evaluate("1 + 1") == 2
    assert SafeEvaluator.evaluate("10 * 5") == 50
    assert SafeEvaluator.evaluate("10 / 2") == 5.0
    assert SafeEvaluator.evaluate("2 ** 3") == 8

def test_safe_evaluator_context():
    context = {"a": 10, "b": 20}
    assert SafeEvaluator.evaluate("a + b", context) == 30
    assert SafeEvaluator.evaluate("b - a", context) == 10

def test_safe_evaluator_functions():
    assert SafeEvaluator.evaluate("abs(-5)") == 5
    assert SafeEvaluator.evaluate("round(5.4)") == 5
    assert SafeEvaluator.evaluate("max(1, 10, 5)") == 10

def test_safe_evaluator_security_breach():
    # Attempt introspection
    assert SafeEvaluator.evaluate("''.__class__") is None
    assert SafeEvaluator.evaluate("pow.__globals__") is None

    # Attempt unauthorized function
    assert SafeEvaluator.evaluate("open('README.md').read()") is None

def test_safe_evaluator_math_module():
    assert SafeEvaluator.evaluate("sqrt(16)") == 4.0
    assert SafeEvaluator.evaluate("ceil(4.2)") == 5
