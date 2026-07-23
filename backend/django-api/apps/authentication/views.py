from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout

class LoginView(APIView):
    """
    Endpoint to authenticate users via username and password without JWT tokens.
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({
                "status": "success",
                "message": "Successfully logged in."
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": "Invalid credentials"
            }, status=status.HTTP_401_UNAUTHORIZED)

class RefreshView(APIView):
    """
    Refresh endpoint (disabled as tokens are removed).
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        return Response({
            "status": "error",
            "message": "Token refresh is not supported."
        }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """
    Endpoint to terminate session and log out the user.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            logout(request)
            return Response({
                "status": "success",
                "message": "Successfully logged out."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
