# tests/unit/test_calculation.py

import uuid
import pytest

from app.models import (
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
)

@pytest.fixture
def user_id():
    """Create a dummy UUID for unit tests."""
    return uuid.uuid4()

@pytest.mark.parametrize(
    "calculation_class,a,b,expected",
    [
        (Addition, 10, 5, 15),
        (Subtraction, 10, 5, 5),
        (Multiplication, 10, 5, 50),
        (Division, 10, 5, 2.0),
    ],
)
def test_calculation_operations(
    calculation_class, a, b, expected, user_id
):
    """Verify each calculation subclass."""
    calculation = calculation_class(
        user_id=user_id,
        a=a,
        b=b,
    )

    assert calculation.get_result() == expected

@pytest.mark.parametrize(
    "operation,expected_class,expected_result",
    [
        ("addition", Addition, 15),
        ("subtraction", Subtraction, 5),
        ("multiplication", Multiplication, 50),
        ("division", Division, 2.0),
    ],
)
def test_calculation_factory(
    operation, expected_class, expected_result, user_id
):
    """Verify that the factory selects the correct subclass."""
    calculation = Calculation.create(
        operation,
        user_id,
        10,
        5,
    )
    assert isinstance(calculation, expected_class)
    assert calculation.result == expected_result
    assert calculation.user_id == user_id

def test_factory_case_insensitive(user_id):
    """Verify uppercase operation names are supported."""
    calculation = Calculation.create(
        "ADDITION",
        user_id,
        10,
        5,
    )
    assert isinstance(calculation, Addition)
    assert calculation.result == 15

def test_factory_invalid_type(user_id):
    """Verify unsupported operations are rejected."""
    with pytest.raises(ValueError, match="Unsupported"):
        Calculation.create("power", user_id, 10, 5)

def test_factory_non_string_type(user_id):
    """Verify non-string operation types are rejected."""
    with pytest.raises(ValueError, match="Invalid calculation type"):
        Calculation.create(123, user_id, 10, 5)

def test_division_by_zero(user_id):
    """Verify the model prevents division by zero."""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        Calculation.create("division", user_id, 10, 0)

def test_abstract_calculation(user_id):
    """Verify the parent class requires subclass logic."""
    calculation = Calculation(
        user_id=user_id,
        a=10,
        b=5,
    )
    with pytest.raises(NotImplementedError):
        calculation.get_result()

def test_calculation_repr(user_id):
    """Verify the calculation string representation."""
    calculation = Addition(
        user_id=user_id,
        a=10,
        b=5,
    )
    assert "Calculation" in repr(calculation)
    assert "a=10" in repr(calculation)
