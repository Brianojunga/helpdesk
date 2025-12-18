from rest_framework import serializers
from .models import Ticket, Company
from django.db import transaction
from django.conf import  settings

User = settings.AUTH_USER_MODEL

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'user', 'first_name', 'last_name', 'email', 'subject', 'description', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        validated_data['company'] = self.context['company']
        return super().create(validated_data)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'slug', 'user']
        read_only_fields = ['id', 'user']

    @transaction.atomic   
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        
        if not user.is_authenticated:
            raise serializers.ValidationError('Authentication is required')
        
        company = Company.objects.create(
            owner=user,
            **validated_data
        )

        user.company = company
        user.role='owner'
        user.save(update_fields=['company', 'role'])

        return company
    