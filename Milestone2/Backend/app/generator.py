import pandas as pd
import random

from app.models import Ticket
from app.urgency import detect_urgency


class TicketGenerator:
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)
        self.df.columns = self.df.columns.str.strip()

    def generate_random_tickets(self, n: int) -> list[Ticket]:

        if n > len(self.df):
            raise ValueError("n is greater than dataset size")

        sampled_df = self.df.sample(
            n=n,
            random_state=random.randint(1, 10000)
        )

        tickets = []

        for idx, row in sampled_df.iterrows():

            subject = row["Ticket Subject"]
            description = row["Ticket Description"]

            urgency_score = detect_urgency(subject + " " + description)

            ticket = Ticket(
                subject=subject,
                description=description,
                urgency_score=urgency_score
            )

            tickets.append(ticket)

        return tickets