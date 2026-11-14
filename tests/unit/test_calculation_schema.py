# tests/unit/test_calculation_schema.py

import uuid
from datetime import datetime
import pytest
from pydantic import ValidationError
from app.schemas.calculation import (
    CalculationCreate,
    CalculationRead,
    CalculationType,
)
from app.models import Calculation

@pytest.mark.parametrize(
    "operation",
    [
        "addition",
        "subtraction",
        "multiplication",
        "division",
    ],
)
def test_valid_calculation_types(operation):
    """Test all supported calculation types."""
    calculation = CalculationCreate(
        a=10,
        b=5,
        type=operation,
    )
    assert calculation.type.value == operation

def test_calculation_operands():
    """Test numeric operands."""
    calculation = CalculationCreate(
        a=10.5,
        b=2.5,
        type="addition",
    )
    assert calculation.a == 10.5
    assert calculation.b == 2.5

def test_calculation_type_enum():
    """Test CalculationType enum values."""
    assert CalculationType.ADDITION.value == "addition"
    assert CalculationType.SUBTRACTION.value == "subtraction"
    assert CalculationType.MULTIPLICATION.value == "multiplication"
    assert CalculationType.DIVISION.value == "division"

def test_invalid_calculation_type():
    """Test unsupported calculation types."""
    with pytest.raises(ValidationError):
        CalculationCreate(
            a=10,
            b=5,
            type="power",
        )

def test_division_by_zero():
    """Test division by zero validation."""
    with pytest.raises(
        ValidationError,
        match="Cannot divide by zero",
    ):
        CalculationCreate(
            a=10,
            b=0,
            type="division",
        )

def test_valid_division():
    """Test division with a nonzero divisor."""
    calculation = CalculationCreate(
        a=10,
        b=2,
        type="division",
    )
    assert calculation.b == 2
    assert calculation.type == CalculationType.DIVISION

def test_missing_operand():
    """Test missing required operand."""
    with pytest.raises(ValidationError):
        CalculationCreate(
            a=10,
            type="addition",
        )

def test_invalid_operand():
    """Test nonnumeric input."""
    with pytest.raises(ValidationError):
        CalculationCreate(
            a="hello",
            b=5,
            type="addition",
        )

def test_case_insensitive_type():
    """Test uppercase calculation type."""
    calculation = CalculationCreate(
        a=10,
        b=5,
        type="ADDITION",
    )
    assert calculation.type == CalculationType.ADDITION

def test_invalid_numeric_type():
    """Test non-string calculation type."""
    with pytest.raises(ValidationError):
        CalculationCreate(
            a=10,
            b=5,
            type=123,
        )

@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_non_finite_operand(value):
    """Test rejection of NaN and infinity."""
    with pytest.raises(ValidationError):
        CalculationCreate(
            a=value,
            b=5,
            type="addition",
        )

def test_calculation_json_serialization():
    """Test schema JSON serialization."""
    calculation = CalculationCreate(
        a=10,
        b=5,
        type="addition",
    )

    data = calculation.model_dump(mode="json")
    assert data["a"] == 10.0
    assert data["b"] == 5.0
    assert data["type"] == "addition"

def test_calculation_read():
    """Test serialization of a SQLAlchemy calculation."""
    user_id = uuid.uuid4()
    calculation_id = uuid.uuid4()
    now = datetime.now()
    calculation = Calculation.create(
        "addition",
        user_id,
        10,
        5,
    )
    calculation.id = calculation_id
    calculation.created_at = now
    calculation.updated_at = now
    response = CalculationRead.model_validate(calculation)
    assert response.id == calculation_id
    assert response.user_id == user_id
    assert response.a == 10
    assert response.b == 5
    assert response.type == CalculationType.ADDITION
    assert response.result == 15
    assert response.created_at == now
    assert response.updated_at == now

def test_calculation_type_enum_input():
    """Test passing a CalculationType enum directly."""
    calculation = CalculationCreate(
        a=10,
        b=5,
        type=CalculationType.ADDITION,
    )
    assert calculation.type == CalculationType.ADDITION
