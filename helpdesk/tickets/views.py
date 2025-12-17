from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from .models import Ticket, Company
from .serializers import TicketSerializer, RegisterSerializer, ProfileSerializer, CompanySerializer
from django.contrib.auth.models import User
from uuid import UUID
from django.shortcuts import get_object_or_404


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    

    def get_queryset(self):
        company = get_object_or_404(
            Company,
            slug = self.kwargs['slug']
        )
        queryset = queryset.filter(company=company)
        
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                return queryset
            # Authenticated users can see their own tickets
            return queryset.filter(user=self.request.user)
        else:
            public_id = self.request.query_params.get('public_id')
            if public_id:
                try:
                   uuid_obj = UUID(public_id, 4)
                except ValueError:
                   return queryset.none()
                return  queryset.filter(public_id = uuid_obj)
        return queryset.none()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['company'] = get_object_or_404(
            Company,
            slug = self.kwargs['slug']
        )
        return context
    
    def perform_create(self, serializer):
        serializer.save()


class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    http_method_names = ['post']


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(user=self.request.user)

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Company.objects.all()
        if hasattr(self.request.user, 'company'):
            return Company.objects.filter(pk=self.request.user.company.pk)
        return Company.objects.none()


