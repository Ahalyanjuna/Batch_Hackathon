from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum
import uuid
import time


class Category(str, Enum):
    billing = "Billing inquiry"
    technical = "Technical issue"
    legal = "Legal inquiry"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Status(str, Enum):
    open = "Open"
    closed = "Closed"
    pending = "Pending Customer Response"


class TicketInput(BaseModel):
    subject: str
    description: str


class Ticket(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject: str
    description: str
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    urgency_score: float = 0.0
    @field_validator("urgency_score")
    def validate_score(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("urgency_score must be between 0 and 1")
        return v
    status: Status = Status.open
    timestamp: float = Field(default_factory=time.time)