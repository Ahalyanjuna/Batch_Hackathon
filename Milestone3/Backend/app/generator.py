import pandas as pd
import random
from app.models import Ticket


class TicketGenerator:

    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)
        self.df.columns = self.df.columns.str.strip()

    def generate_random_tickets(self, n: int):

        sampled_df = self.df.sample(
            n=n,
            random_state=random.randint(1, 10000)
        )

        tickets = []

        for _, row in sampled_df.iterrows():

            ticket = Ticket(
                subject=row["Ticket Subject"],
                description=row["Ticket Description"]
            )

            tickets.append(ticket)

        return tickets

