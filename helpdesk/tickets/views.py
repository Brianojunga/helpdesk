from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Ticket
from .serializers import TicketSerializer

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Ticket.objects.all()
        if self.request.user.is_authenticated:
            # Authenticated users can see their own tickets
            queryset = queryset.filter(user=self.request.user)
        else:
            # Non-authenticated users can't list tickets (or handle differently)
            queryset = Ticket.objects.none()
        return queryset

    def perform_create(self, serializer):
        serializer.save()
