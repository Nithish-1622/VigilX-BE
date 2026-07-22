from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

class LoginView(TokenObtainPairView):
    """
    Subclass of simplejwt's TokenObtainPairView to authenticate users 
    and retrieve JWT access and refresh tokens.
    """
    permission_classes = (AllowAny,)

class RefreshView(TokenRefreshView):
    """
    Subclass of simplejwt's TokenRefreshView to rotate access tokens.
    """
    permission_classes = (AllowAny,)

class LogoutView(APIView):
    """
    Endpoint to terminate session and log out the user.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            from rest_framework_simplejwt.tokens import RefreshToken
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                "status": "success",
                "message": "Successfully logged out."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
