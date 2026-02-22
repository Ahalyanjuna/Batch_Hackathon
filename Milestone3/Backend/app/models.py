from pydantic import BaseModel, Field
import uuid
import time


class Ticket(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject: str
    description: str
    timestamp: float = Field(default_factory=time.time)