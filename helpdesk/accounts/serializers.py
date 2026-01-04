from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()

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
        return data


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
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'created_at', 'updated_at']
        read_only_fields = ['id']

class AssignAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']

    def validate_role(self, value):
        if value not in ['admin', 'agent', 'customer']:
            raise serializers.ValidationError("You can only assign the agent role.")
        return value

    