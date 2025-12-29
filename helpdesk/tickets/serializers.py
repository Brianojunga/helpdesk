from rest_framework import serializers
from .models import Ticket, Company, TicketResolution
from django.db import transaction
from django.conf import  settings


User = settings.AUTH_USER_MODEL

class TicketResolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketResolution
        fields = ['message', 'created_at']


class TicketSerializer(serializers.ModelSerializer):
    resolution = TicketResolutionSerializer(read_only=True)
    resolution_message = serializers.CharField(
        write_only=True, 
        required=False, 
        allow_blank=True,
        help_text="Resolution message when closing the ticket"
    )
    
    class Meta:
        model = Ticket
        fields = ['id', 'user', 'first_name', 
                  'last_name', 'email', 'subject', 
                  'description', 'status', 'created_at',
                  'public_id', 'assigned_to', 'updated_at', 
                  'resolution_message', 'resolution'
                ]
        read_only_fields = ['public_id', 'user', 'created_at', 'updated_at', 'resolution']

    def validate(self, data):
        new_status = data.get('status')
        if new_status == 'closed': 
            resolution_message = data.get('resolution_message')
            #for updating checks if the instance exists
            if self.instance and self.instance.status != 'closed':
                 if not resolution_message or not resolution_message.strip():
                    raise serializers.ValidationError({
                        'resolution_message': 'Resolution message is required when closing a ticket.'
                    })
        return data
    
    def create(self, validated_data):
        #remove the message because it does not exist in ticket model
        validated_data.pop('resolution_message', None)
        return super().create(validated_data)
    
    @transaction.atomic
    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get('status', old_status)

        if old_status == new_status:
            return
        
        #remove the message before updating the message
        resolution_message = validated_data.pop('resolution_message', None)

        instance = super().update(instance, validated_data)

        
        #continue from here not done
        if new_status == 'closed':
            TicketResolution.objects.create(
                ticket=instance,
                message=resolution_message
            )
        return instance


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id']

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        if not user.is_authenticated:
            raise serializers.ValidationError('Authentication is required')
        return data
        
  
