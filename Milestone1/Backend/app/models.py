from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import uuid
import time

class Category(str, Enum):
    billing = "Billing inquiry"
    technical = "Technical"
    legal = "Legal"

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
    urgency_score: float = 0.0  # critical=1.0, high=0.75, medium=0.5, low=0.25
    status: Status = Status.open
    timestamp: float = Field(default_factory=time.time)