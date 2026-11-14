# tests/integration/test_calculation.py

import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.calculation import (
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
)
from app.schemas.calculation import CalculationCreate

def test_create_calculation(db_session, test_user):
    """Test saving a calculation in PostgreSQL."""
    calculation = Calculation.create(
        "addition",
        test_user.id,
        10,
        5,
    )
    db_session.add(calculation)
    db_session.commit()
    db_session.refresh(calculation)

    assert calculation.id is not None
    assert calculation.a == 10
    assert calculation.b == 5
    assert calculation.type == "addition"
    assert calculation.result == 15
    assert calculation.user_id == test_user.id

def test_retrieve_calculation(db_session, test_user):
    """Test retrieving a saved calculation."""
    calculation = Calculation.create(
        "multiplication",
        test_user.id,
        6,
        7,
    )
    db_session.add(calculation)
    db_session.commit()
    saved = db_session.get(Calculation, calculation.id)
    assert saved is not None
    assert saved.result == 42
    assert isinstance(saved, Multiplication)


@pytest.mark.parametrize(
    "operation,expected_class,expected_result",
    [
        ("addition", Addition, 15),
        ("subtraction", Subtraction, 5),
        ("multiplication", Multiplication, 50),
        ("division", Division, 2.0),
    ],
)
def test_polymorphic_calculation(
    db_session, test_user, operation, expected_class, expected_result
):
    """Test polymorphic calculations stored in PostgreSQL."""
    calculation = Calculation.create(
        operation,
        test_user.id,
        10,
        5,
    )
    db_session.add(calculation)
    db_session.commit()
    calculation_id = calculation.id
    db_session.expunge_all()
    saved = db_session.get(Calculation, calculation_id)

    assert saved is not None
    assert isinstance(saved, expected_class)
    assert saved.result == expected_result
    assert saved.get_result() == expected_result


def test_user_calculation_relationship(db_session, test_user):
    """Test the relationship between users and calculations."""
    calculation = Calculation.create(
        "addition",
        test_user.id,
        20,
        10,
    )
    db_session.add(calculation)
    db_session.commit()
    db_session.refresh(test_user)
    assert calculation in test_user.calculations
    assert calculation.user.id == test_user.id

def test_invalid_calculation_type(db_session, test_user):
    """Test rejection of an unsupported calculation type."""
    with pytest.raises(ValueError):
        Calculation.create(
            "power",
            test_user.id,
            10,
            5,
        )

def test_division_by_zero(db_session, test_user):
    """Test rejection of division by zero."""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        Calculation.create(
            "division",
            test_user.id,
            10,
            0,
        )

def test_invalid_foreign_key(db_session):
    """Test rejection of a nonexistent user UUID."""
    calculation = Calculation.create(
        "addition",
        uuid.uuid4(),
        10,
        5,
    )

    db_session.add(calculation)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_calculation_schema_to_database(db_session, test_user):
    """Test validated Pydantic input saved through SQLAlchemy."""
    data = CalculationCreate(
        a=20,
        b=4,
        type="division",
    )
    calculation = Calculation.create(
        data.type.value,
        test_user.id,
        data.a,
        data.b,
    )
    db_session.add(calculation)
    db_session.commit()
    db_session.refresh(calculation)
    assert calculation.a == 20
    assert calculation.b == 4
    assert calculation.type == "division"
    assert calculation.result == 5.0
