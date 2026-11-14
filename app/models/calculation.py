
# app/models/calculation.py

"""
Calculation models using SQLAlchemy polymorphic inheritance.
"""

from datetime import datetime
import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declared_attr

from app.database import Base

class AbstractCalculation:
    """
    Defines common attributes and methods for calculations.
    """

    @declared_attr
    def __tablename__(cls):
        return "calculations"

    @declared_attr
    def id(cls):
        return Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            nullable=False
        )

    @declared_attr
    def user_id(cls):
        return Column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True
        )

    @declared_attr
    def a(cls):
        return Column(Float, nullable=False)

    @declared_attr
    def b(cls):
        return Column(Float, nullable=False)

    @declared_attr
    def type(cls):
        return Column(
            String(50),
            nullable=False,
            index=True
        )

    @declared_attr
    def result(cls):
        return Column(Float, nullable=True)

    @declared_attr
    def created_at(cls):
        return Column(
            DateTime,
            default=datetime.utcnow,
            nullable=False
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False
        )

    @declared_attr
    def user(cls):
        return relationship(
            "User",
            back_populates="calculations"
        )

    @classmethod
    def create(cls, calculation_type, user_id, a, b):
        """
        Factory method to create the correct calculation type.
        """
        calculation_classes = {
            "addition": Addition,
            "subtraction": Subtraction,
            "multiplication": Multiplication,
            "division": Division
        }

        if not isinstance(calculation_type, str):
            raise ValueError("Invalid calculation type")

        calculation_class = calculation_classes.get(
            calculation_type.lower()
        )

        if calculation_class is None:
            raise ValueError(
                f"Unsupported calculation type: {calculation_type}"
            )

        calculation = calculation_class(
            user_id=user_id,
            a=a,
            b=b
        )

        calculation.result = calculation.get_result()

        return calculation

    def get_result(self):
        raise NotImplementedError(
            "Subclasses must implement get_result()"
        )

    def __repr__(self):
        return (
            f"<Calculation(type={self.type}, "
            f"a={self.a}, b={self.b})>"
        )


class Calculation(AbstractCalculation, Base):
    """
    Parent calculation model using single-table inheritance.
    """

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "calculation"
    }


class Addition(Calculation):
    __mapper_args__ = {
        "polymorphic_identity": "addition"
    }

    def get_result(self):
        return self.a + self.b


class Subtraction(Calculation):
    __mapper_args__ = {
        "polymorphic_identity": "subtraction"
    }

    def get_result(self):
        return self.a - self.b


class Multiplication(Calculation):
    __mapper_args__ = {
        "polymorphic_identity": "multiplication"
    }

    def get_result(self):
        return self.a * self.b


class Division(Calculation):
    __mapper_args__ = {
        "polymorphic_identity": "division"
    }

    def get_result(self):
        try:
            return self.a / self.b
        except ZeroDivisionError:
            raise ValueError("Cannot divide by zero.") from None
