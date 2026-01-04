from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Ticket, Company
from .serializers import TicketSerializer, CompanySerializer
from django.contrib.auth import get_user_model
from uuid import UUID
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import action
from accounts.permissions import CanAssignAgent
from .permissions import CanAccessTicketResolution
from rest_framework.filters import OrderingFilter


User =  get_user_model()

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    ordering_fields = ["priority"]
    ordering = ["-priority"]
    

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Ticket.objects.none()
        
        company = get_object_or_404(
            Company,
            # slug=self.kwargs['slug']
            slug = self.kwargs.get('slug')
        )

        queryset = Ticket.objects.filter(company=company)
        user = self.request.user

        if user.is_authenticated:
            if user.is_superuser or user.role in ['owner', 'admin']:
                return queryset
            if user.role == "agent":
                # Agents can see tickets assigned to them
                return queryset.filter(assigned_to=user)
            # Authenticated users can see their own tickets
            return queryset.filter(user=user)
        else:
            public_id = self.request.query_params.get('public_id')
            if public_id:
                try:
                   uuid_obj = UUID(public_id, 4)
                except ValueError:
                   return queryset.none()
                return  queryset.filter(public_id = uuid_obj)
        return queryset.none()
    
    def perform_create(self, serializer):

        company = get_object_or_404(
            Company,
            slug=self.kwargs['slug']
        )
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(
            company=company,
            user=user
        )
    
    @action(detail=True, methods=['patch'], permission_classes=[CanAssignAgent])
    def assign_agent(self, request, pk=None, slug=None):
        ticket = self.get_object()
        agent_id = request.data.get('assigned_to')
        agent = get_object_or_404(User, pk=agent_id)
        if agent.company != ticket.company:
            return Response(
                {'detail' : 'The agent does not belong to the same company as the ticket.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if ticket.assigned_to == agent:
            return Response(
                {'detail' : 'This agent is already assigned to this ticket.'},
                status = status.HTTP_400_BAD_REQUEST
            )
        if ticket.status == 'closed':
            return Response(
                {'detail' : 'Cannot assign agent to a closed ticked.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ticket.assigned_to = agent
        ticket.status = 'in_progress'
        ticket.save(update_fields=['assigned_to', 'status'])
        return Response(
            {'detail' : f'{agent.username} has been assigned to the ticket'},
            status=status.HTTP_200_OK
            )

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Company.objects.all()
        if user.company and user.role=='owner':
            return Company.objects.filter(pk=user.company.pk)
        return Company.objects.none()
    
    @transaction.atomic   
    def create(self, request, *args, **kwargs):
        user =self.request.user
        
        if user.company and user.role == 'owner':
            return Response(
                {'error': 'You already own a company. Each user can only own one company.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = request.data.copy()
        data.pop('resolution_message', None)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        company = serializer.save()

        user.company = company
        user.role='owner'
        user.save(update_fields=['company', 'role'])

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TicketResolutionViewset(viewsets.ModelViewSet):
    queryset = Ticket.objects.filter(status='closed').select_related('resolution')
    serializer_class = TicketSerializer
    permissson_classes = [CanAccessTicketResolution]
    http_method_names = ['get']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Ticket.objects.none()
        
        company = get_object_or_404(
            Company,
            slug=self.kwargs.get('slug')
        )
        user = self.request.user
        if user.company == company and user.role in ['owner', 'admin', 'agent']:
            return Ticket.objects.filter(
                company=company, 
                status='closed'
                ).select_related('resolution')
        if user:
            return Ticket.objects.filter(
                company=company,
                status='closed',
                user=user
            ).select_related('resolution')
        return Ticket.objects.none()
        