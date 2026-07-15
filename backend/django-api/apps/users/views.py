from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from api.serializers.auth import UserSerializer, RegisterSerializer
from api.permissions.rbac import IsSupervisor

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage user profiles.
    Only Supervisors have listing, creation, and modification permissions on the User list.
    Every authenticated user can request details about themselves using the '/me' action.
    """
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterSerializer
        return UserSerializer

    def get_permissions(self):
        # Restrict standard list and CRUD operations to Supervisors only
        if self.action in ['list', 'create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSupervisor()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='me')
    def me(self, request):
        """
        Returns the profile information of the current logged-in user.
        """
        serializer = UserSerializer(request.user, context={'request': request})
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
