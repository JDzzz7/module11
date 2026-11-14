# app/schemas/calculation.py

"""
Pydantic schemas for calculation validation and serialization.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

class CalculationType(str, Enum):
    """
    Supported calculation operations.
    """

    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"

class CalculationBase(BaseModel):
    """
    Common fields and validation for calculations.
    """
    a: float = Field(
        ...,
        allow_inf_nan=False,
        description="First operand",
        examples=[10.0],
    )

    b: float = Field(
        ...,
        allow_inf_nan=False,
        description="Second operand",
        examples=[5.0],
    )

    type: CalculationType = Field(
        ...,
        description="Type of calculation",
        examples=["addition"],
    )

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, value):
        """
        Validate and normalize the calculation type.
        """
        if isinstance(value, CalculationType):
            return value

        if not isinstance(value, str):
            raise ValueError("Calculation type must be a string")

        value = value.lower()

        allowed = {item.value for item in CalculationType}

        if value not in allowed:
            raise ValueError(
                f"Type must be one of: {', '.join(sorted(allowed))}"
            )

        return value

    @model_validator(mode="after")
    def validate_operands(self):
        """
        Validate operands before performing calculations.
        """
        if self.type == CalculationType.DIVISION and self.b == 0:
            raise ValueError("Cannot divide by zero")

        return self

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {"a": 10, "b": 5, "type": "addition"},
                {"a": 10, "b": 2, "type": "division"},
            ]
        },
    )

class CalculationCreate(CalculationBase):
    """
    Schema for creating a calculation.
    """
    pass

class CalculationRead(CalculationBase):
    """
    Schema for reading a calculation from the database.
    """

    id: UUID
    user_id: UUID
    result: float | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

CalculationResponse = CalculationRead
