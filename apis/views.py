from django.contrib.auth import login, logout
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
        Login a user.

        Login to the API using a username and password. The response will assign a token as a cookie to the user.
        All of this operations are handled by the Django authentication framework.
        """
        serializer = serializers.LoginSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response({'detail': 'Login successfully.'}, status=status.HTTP_200_OK)


class LogoutView(views.APIView):
    # This view should be accessible only for authenticated users.
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema()
    def post(self, request):
        """
        Logout a user.

        Logout from the API. The response will remove the token cookie from the user.
        All of this operations are handled by the Django authentication framework.
        """
        logout(request)
        return Response({'detail': 'Logout successfully.'}, status=status.HTTP_200_OK)


class UserProfileView(views.APIView):
    permissions_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={
        200: serializers.UserProfileSerializer,
        401: 'User is not authenticated.',
    })
    def get(self, request):
        """
        Get the user profile of current user.

        Get the user profile of the current user. The response will contain
        the user's username, email and other detail that's show in profile page.
        """
        if not request.user.is_authenticated:
            return Response({'detail': 'User is not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = serializers.UserProfileSerializer(request.user.profile)
        return Response({'detail': 'Get current user profile successfully.', 'result': serializer.data},
                        status=status.HTTP_200_OK)


class AreasView(views.APIView):
    permissions_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: serializers.AreaSerializer(many=True)})
    def get(self, request):
        """
        Get all areas.

        Get a list of all areas.
        """
        serializer = serializers.AreaSerializer(Area.objects.all(), many=True)
        return Response({'detail': 'Get all election area successfully', 'result': serializer.data},
                        status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=serializers.AreaSerializer, responses={
        201: serializers.AreaSerializer,
        400: serializers.AreaSerializer,
        401: serializers.ErrorSerializer(detail='You do not have permission to perform this action.')
    })
    def post(self, request):
        """
        Create a new area.

        Create a new area for election. This action is only allowed for staff user.
        """
        if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
            serializer = serializers.AreaSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'detail': 'Create new area successfully', 'result': serializer.data},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': 'Create new area failed', 'errors': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Create new area failed',
                             'errors': {'detail': 'You do not have permission to perform this action.'}},
                            status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(request_body=serializers.UpdateAreaSerializer, responses={
        200: serializers.AreaSerializer,
        400: serializers.UpdateAreaSerializer,
        401: serializers.ErrorSerializer(detail='You do not have permission to perform this action.')
    })
    def put(self, request):
        """
        Update an area.

        Update a target area information for election. This action is only allowed for staff user.
        Note : All field except area_id are optional. The system will only update the field that send and not empty.
        """
        if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
            serializer = serializers.UpdateAreaSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    area = Area.objects.get(id=serializer.validated_data['area_id'])
                except Area.DoesNotExist:
                    return Response({'detail': 'Update area failed', 'errors': {'detail': 'Area does not exist.'}})
                data_key_list = serializer.validated_data.keys()
                if 'name' in data_key_list:
                    if serializer.validated_data['name'] != '':
                        area.name = serializer.validated_data['name']
                if 'description' in data_key_list:
                    if serializer.validated_data['description'] != '':
                        area.description = serializer.validated_data['description']
                area.save()
                return Response({'detail': 'Update area successfully', 'result': serializers.AreaSerializer(area).data},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': 'Update area failed', 'errors': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Update area failed',
                             'errors': {'detail': 'You do not have permission to perform this action.'}},
                            status=status.HTTP_401_UNAUTHORIZED)


class CandidatesView(views.APIView):
    permissions_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: serializers.GetCandidateSerializer(many=True)})
    def get(self, request):
        """
        Get all candidates.

        Get a list of all candidates.
        """
        serializer = serializers.GetCandidateSerializer(Candidate.objects.all(), many=True,
                                                        context={'request': self.request})
        return Response({'detail': 'Get all candidates successfully', 'result': serializer.data},
                        status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=serializers.CreateCandidateSerializer, responses={
        201: serializers.GetCandidateSerializer,
        400: serializers.CreateCandidateSerializer,
        401: serializers.ErrorSerializer(detail='You do not have permission to perform this action.')
    })
    def post(self, request):
        """
        Add a new candidate. (Currently not support upload image)

        Add a new candidate for election. This action is only allowed for staff user.
        """
        serializer = serializers.CreateCandidateSerializer(data=request.data, context={'request': self.request})
        if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
            if serializer.is_valid():
                # Change area_id to area object
                try:
                    area = Area.objects.get(id=serializer.validated_data['area_id'])
                    serializer.validated_data['area'] = area
                    serializer.save()
                    return Response({'detail': 'Create new candidate successfully',
                                     'result': serializers.GetCandidateSerializer(serializer.instance, context={
                                         'request': self.request}).data}, status=status.HTTP_201_CREATED)
                except Area.DoesNotExist:
                    return Response(
                        {'detail': 'Create new candidate failed', 'errors': {'area_id': 'Area does not exist.'}},
                        status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'Create new candidate failed', 'errors': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Create new candidate failed',
                             'errors': {'detail': 'You do not have permission to perform this action.'}},
                            status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(request_body=serializers.UpdateCandidateSerializer, responses={
        201: serializers.GetCandidateSerializer,
        400: serializers.UpdateCandidateSerializer,
        401: serializers.ErrorSerializer(detail='You do not have permission to perform this action.')
    })
    def put(self, request):
        """
        Update a candidate. (Currently not support upload image)

        Update a target candidate information for election. This action is only allowed for staff user.
        Note : All field except candidate_id are optional. The system will only update the field that send and not empty.
        """
        serializer = serializers.UpdateCandidateSerializer(data=request.data, context={'request': self.request})
        if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
            if serializer.is_valid():
                try:
                    candidate = Candidate.objects.get(id=serializer.validated_data['candidate_id'])
                except Candidate.DoesNotExist:
                    return Response({'detail': 'Update candidate failed', 'errors': {'detail': 'Candidate does not exist.'}})
                data_key_list = serializer.validated_data.keys()
                if 'name' in data_key_list:
                    if serializer.validated_data['name'] != '':
                        candidate.name = serializer.validated_data['name']
                if 'description' in data_key_list:
                    if serializer.validated_data['description'] != '':
                        candidate.description = serializer.validated_data['description']
                if 'area_id' in data_key_list:
                    if serializer.validated_data['area_id'] != '':
                        try:
                            area = Area.objects.get(id=serializer.validated_data['area_id'])
                            candidate.area = area
                        except Area.DoesNotExist:
                            return Response({'detail': 'Update candidate failed',
                                             'errors': {'area_id': 'Area does not exist.'}})
                candidate.save()
                return Response({'detail': 'Update candidate successfully',
                                 'result': serializers.GetCandidateSerializer(candidate, context={
                                     'request': self.request}).data}, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': 'Update candidate failed', 'errors': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Update candidate failed',
                             'errors': {'detail': 'You do not have permission to perform this action.'}},
                            status=status.HTTP_401_UNAUTHORIZED)


class ElectionsView(views.APIView):
    permissions_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: serializers.GetElectionSerializer(many=True)})
    def get(self, request):
        """
        Get all elections.

        Get a list of all elections.
        """
        serializer = serializers.GetElectionSerializer(Election.objects.all(), many=True,
                                                       context={'request': self.request})
        return Response({'detail': 'Get all elections successfully', 'result': serializer.data},
                        status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=serializers.CreateElectionSerializer, responses={
        201: serializers.GetElectionSerializer,
        400: serializers.CreateElectionSerializer,
        401: serializers.ErrorSerializer(detail='You do not have permission to perform this action.')
    })
    def post(self, request):
        """
        Start a new election. (Currently not support upload image)

        Start a new election. This action is only allowed for staff user.
        """
        serializer = serializers.CreateElectionSerializer(data=request.data, context={'request': self.request})
        if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
            if serializer.is_valid():
                serializer.save()
                return Response({'detail': 'Create new election successfully',
                                 'result': serializers.GetElectionSerializer(serializer.instance, context={
                                     'request': self.request}).data}, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': 'Create new election failed', 'errors': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Create new election failed',
                             'errors': {'detail': 'You do not have permission to perform this action.'}},
                            status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(request_body=serializers.UpdateElectionSerializer, responses={
        201: serializers.GetElectionSerializer,
        400: serializers.UpdateElectionSerializer,
        401: serializers.ErrorSerializer(detail='You do not have permission to perform this action.')
    })
    def put(self, request):
        """
        Update an election. (Currently not support upload image)

        Update a target election information. This action is only allowed for staff user.
        Note : All field except election_id are optional. The system will only update the field that send and not empty.

        For election, the API will also do like the edit election page, To make the election fair,
        the system will only allow to make some change on not essential information of the election only.
        """
        serializer = serializers.UpdateElectionSerializer(data=request.data, context={'request': self.request})
        if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
            if serializer.is_valid():
                try:
                    election = Election.objects.get(id=serializer.validated_data['election_id'])
                except Election.DoesNotExist:
                    return Response({'detail': 'Update election failed', 'errors': {'detail': 'Election does not exist.'}})
                data_key_list = serializer.validated_data.keys()
                if 'description' in data_key_list:
                    if serializer.validated_data['description'] != '':
                        election.description = serializer.validated_data['description']
                election.save()
                return Response({'detail': 'Update election successfully',
                                 'result': serializers.GetElectionSerializer(election, context={
                                     'request': self.request}).data}, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': 'Update election failed', 'errors': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Update election failed',
                             'errors': {'detail': 'You do not have permission to perform this action.'}},
                            status=status.HTTP_401_UNAUTHORIZED)