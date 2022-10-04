from django.contrib.auth import login
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework import views
from rest_framework.response import Response

from apps.models import Area, Candidate, Election
from . import serializers


class LoginView(views.APIView):
    # This view should be accessible also for unauthenticated users.
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=serializers.LoginSerializer, responses={200: serializers.LoginSerializer})
    def post(self, request):
        """
        Login using username and password to system using Django auth framework.
        """
        serializer = serializers.LoginSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response({'detail': 'Login successfully.'}, status=status.HTTP_200_OK)


class UserProfileView(views.APIView):
    permissions_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: serializers.UserProfileSerializer})
    def get(self, request):
        """
        Get the user profile of the authenticated user.
        """
        serializer = serializers.UserProfileSerializer(request.user.profile)
        return Response({'detail': 'Get current user profile successfully.', 'result': serializer.data}, status=status.HTTP_200_OK)


class AreasView(views.APIView):
    permissions_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: serializers.AreaSerializer(many=True)})
    def get(self, request):
        """
        Get all areas.
        """
        serializer = serializers.AreaSerializer(Area.objects.all(), many=True)
        return Response({'detail': 'Get all election area successfully', 'result': serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=serializers.AreaSerializer, responses={
        201: serializers.AreaSerializer,
        400: serializers.AreaSerializer,
        401: serializers.ErrorSerializer(detail='You do not have permission to perform this action.')
    })
    def post(self, request):
        """
        Create a new area.
        """
        if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
            serializer = serializers.AreaSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'detail': 'Create new area successfully', 'result': serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': 'Create new area failed', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Create new area failed', 'errors': {'detail': 'You do not have permission to perform this action.'}}, status=status.HTTP_401_UNAUTHORIZED)


class CandidatesView(views.APIView):
    permissions_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: serializers.CandidateSerializer(many=True)})
    def get(self, request):
        """
        Get all candidates.
        """
        serializer = serializers.CandidateSerializer(Candidate.objects.all(), many=True, context={'request': self.request})
        return Response({'detail': 'Get all candidates successfully', 'result': serializer.data}, status=status.HTTP_200_OK)
    


class GetAllElectionsView(views.APIView):
    permissions_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: serializers.ElectionSerializer(many=True)})
    def get(self, request):
        """
        Get all elections.
        """
        serializer = serializers.ElectionSerializer(Election.objects.all(), many=True, context={'request': self.request})
        return Response({'detail': 'Get all elections successfully', 'result': serializer.data}, status=status.HTTP_200_OK)