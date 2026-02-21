import pandas as pd
import random
from app.models import Ticket
from app.queue_manager import ticket_queue
from app.urgency import detect_urgency


class TicketGenerator:
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)
        self.df.columns = self.df.columns.str.strip()

    def generate_random_tickets(self, n: int) -> list[Ticket]:
        """
        Randomly sample n rows from dataset and convert to Ticket objects
        """
        if n > len(self.df):
            raise ValueError("n is greater than dataset size")

        sampled_df = self.df.sample(n=n, random_state=random.randint(1, 10000))

        tickets = []

        for idx, row in sampled_df.iterrows():

            ticket = Ticket(
                id=str(idx),
                subject=row["Ticket Subject"],
                description=row["Ticket Description"]
            )

            ticket.urgency_score = detect_urgency(ticket.description)
            tickets.append(ticket)

        return tickets

    def push_to_queue(self, tickets: list[Ticket]):
        """
        Push generated tickets into global priority queue
        """
        for t in tickets:
            ticket_queue.push(t)