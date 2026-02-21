import heapq
from app.models import Ticket

class PriorityQueue:
    def __init__(self):
        self._queue = []
        self._counter = 0  # tiebreaker to avoid comparing Ticket objects

    def push(self, ticket: Ticket):
        priority = -ticket.urgency_score  # higher score first
        heapq.heappush(self._queue, (priority, self._counter, ticket))
        self._counter += 1

    def pop(self) -> Ticket:
        if self.is_empty():
            raise IndexError("Queue is empty")
        _, _, ticket = heapq.heappop(self._queue)
        return ticket

    def peek(self) -> Ticket:
        if self.is_empty():
            raise IndexError("Queue is empty")
        _, _, ticket = self._queue[0]
        return ticket

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def size(self) -> int:
        return len(self._queue)

    def all_tickets(self) -> list[Ticket]:
        # Return tickets sorted by priority without removing them
        return [ticket for _, _, ticket in sorted(self._queue)]

# Single shared instance
ticket_queue = PriorityQueue()