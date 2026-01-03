from django.shortcuts import render
from rest_framework import viewsets
from .serializers import RegisterSerializer, ProfileSerializer, AssignAgentSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .permissions import CanAssignAgent
from django.shortcuts import get_object_or_404

# Create your views here.
User = get_user_model()

class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    http_method_names = ['post']


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        if hasattr(user, 'company') and user.role in ['owner', 'admin']:
            return User.objects.filter(company=user.company)
        return User.objects.filter(id=user.id)
    
    @action(detail=True, methods=['post'], permission_classes=[CanAssignAgent])
    def assign_role(self, request, pk=None):
        user_to_update = get_object_or_404(User, pk=pk)
        serializer = AssignAgentSerializer(
            user_to_update,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        new_role = serializer.validated_data['role']
        actor = request.user

        if actor == user_to_update:
            return Response(
                {"detail": "You cannot change your own role."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if new_role == 'admin' and actor.role != 'owner':
            return Response(
                {"detail": "Only owners can assign admin role."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer.save(
            company=actor.company
        )
        return Response(
            {
                "detail": f"User role changed to {new_role}.",
                "user": serializer.data
            },
            status=status.HTTP_200_OK
        )
