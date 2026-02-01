from app.repositories.ticket_repository import TicketRepository


class TicketService:
    def __init__(self, ticket_repository: TicketRepository):
        self.ticket_repository = ticket_repository

    def create_ticket(self, ticket_create_request):
        return self.ticket_repository.create_ticket(ticket_create_request)
