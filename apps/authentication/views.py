from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer
)
from .models import User


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Creates a new user account with the provided information.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        operation_description="Register a new user account",
        responses={
            201: openapi.Response(
                description="User created successfully",
                schema=UserProfileSerializer
            ),
            400: "Bad Request - Validation errors"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """
    API endpoint for user login.
    Authenticates user and returns JWT tokens.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserLoginSerializer

    @swagger_auto_schema(
        operation_description="Login with username and password to get JWT tokens",
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "user": {
                            "id": "uuid",
                            "username": "john_doe",
                            "email": "john@example.com"
                        },
                        "tokens": {
                            "refresh": "refresh_token_here",
                            "access": "access_token_here"
                        }
                    }
                }
            ),
            400: "Bad Request - Invalid credentials"
        }
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    """
    API endpoint for user logout.
    Blacklists the refresh token to prevent further use.
    """
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Logout user by blacklisting the refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
            }
        ),
        responses={
            200: "Logout successful",
            400: "Bad Request - Invalid or missing token"
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {'message': 'Logout successful'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Invalid token or token already blacklisted'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to retrieve and update the current user's profile.
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(
        operation_description="Get current user profile",
        responses={
            200: UserProfileSerializer
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update current user profile",
        request_body=UserUpdateSerializer,
        responses={
            200: UserProfileSerializer,
            400: "Bad Request - Validation errors"
        }
    )
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update current user profile",
        request_body=UserUpdateSerializer,
        responses={
            200: UserProfileSerializer,
            400: "Bad Request - Validation errors"
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserProfileSerializer


class ChangePasswordView(APIView):
    """
    API endpoint for changing user password.
    """
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Change user password",
        request_body=ChangePasswordSerializer,
        responses={
            200: "Password changed successfully",
            400: "Bad Request - Validation errors"
        }
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {'message': 'Password changed successfully'},
            status=status.HTTP_200_OK
        )
