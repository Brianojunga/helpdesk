from rest_framework import serializers
from .models import Ticket, Company
from django.contrib.auth.models import User

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
    
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate(self, data):
        email = data.get('email', None)
        username = data.get('username')
        if not email:
            raise serializers.ValidationError("Email is required.")
        
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email is already in use.")
        
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username is already taken.")


    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'slug']
        
    