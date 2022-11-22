from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework import views
from rest_framework.response import Response

from apps.models import NewArea, NewCandidate, NewElection, VoteCheck, VoteResultCandidate, VoteResultParty, NewParty
from apps.utils import is_there_ongoing_election, check_election_status, calculate_election_party_result
from . import serializers
from .serializers import VoteSerializer, VoteCheckSerializer


class LoginView(views.APIView):
    # This view should be accessible also for unauthenticated users.
    permission_classes = [permissions.AllowAny]

    @csrf_exempt
    @swagger_auto_schema(request_body=serializers.LoginSerializer, responses={200: serializers.UserProfileSerializer})
    def post(self, request):
        """
        Login a user.

        Login to the API using a username and password. The response will assign a token as a cookie to the user.
        All of this operations are handled by the Django authentication framework. The response is user profile
        so there is no need to do redundant request to profile API.
        """
        serializer = serializers.LoginSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        serializer = serializers.UserProfileSerializer(request.user.newprofile, context={'request': self.request})
        return Response({'detail': 'Login successfully', 'result': serializer.data},
                        status=status.HTTP_200_OK)


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
        serializer = serializers.UserProfileSerializer(request.user.newprofile, context={'request': self.request})
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
        serializer = serializers.AreaSerializer(NewArea.objects.all().order_by('id'), many=True)
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
                    area = NewArea.objects.get(id=serializer.validated_data['area_id'])
                except NewArea.DoesNotExist:
                    return Response({'detail': 'Update area failed', 'errors': {'detail': 'Area does not exist.'}})
                data_key_list = serializer.validated_data.keys()
                if 'name' in data_key_list:
                    if serializer.validated_data['name'] != '':
                        area.name = serializer.validated_data['name']
                if 'population' in data_key_list:
                    if serializer.validated_data['population'] != '':
                        area.description = serializer.validated_data['population']
                if 'number_of_voters' in data_key_list:
                    if serializer.validated_data['number_of_voters'] != '':
                        area.number_of_voters = serializer.validated_data['number_of_voters']
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


class AreaDetailView(views.APIView):
    permissions_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={
        404: serializers.ErrorSerializer(detail='Area does not exist.')
    })
    def get(self, request, area_id):
        """
        Get detail of an area.

        Get the full detail of the target area with list of candidates in that area.
        """
        try:
            area = NewArea.objects.get(id=area_id)
            area_serializer = serializers.AreaSerializer(area, context={'request': self.request})
            candidate_serializer = serializers.GetCandidateSerializer(
                NewCandidate.objects.filter(area=area).order_by('id'), many=True,
                context={'request': self.request})
            return Response({'detail': 'Get area detail successfully', 'result': {
                'area': area_serializer.data,
                'candidates': candidate_serializer.data
            }}, status=status.HTTP_200_OK)
        except NewArea.DoesNotExist:
            return Response({'detail': 'Get area detail failed', 'errors': {'detail': 'Area does not exist.'}},
                            status=status.HTTP_404_NOT_FOUND)


class CandidatesView(views.APIView):
    permissions_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: serializers.GetCandidateSerializer(many=True)})
    def get(self, request):
        """
        Get all candidates.

        Get a list of all candidates.
        """
        serializer = serializers.GetCandidateSerializer(NewCandidate.objects.all().order_by('id'), many=True,
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
                    user = User.objects.get(id=serializer.validated_data['user_id'])
                    serializer.validated_data['user'] = user
                except User.DoesNotExist:
                    return Response({'detail': 'Create candidate failed', 'errors': {'user_id': 'User does not exist.'}}
                                    , status=status.HTTP_400_BAD_REQUEST)
                try:
                    area = NewArea.objects.get(id=serializer.validated_data['area_id'])
                    serializer.validated_data['area'] = area
                    serializer.save()
                    return Response({'detail': 'Create new candidate successfully',
                                     'result': serializers.GetCandidateSerializer(serializer.instance, context={
                                         'request': self.request}).data}, status=status.HTTP_201_CREATED)
                except NewArea.DoesNotExist:
                    return Response(
                        {'detail': 'Create new candidate failed', 'errors': {'area_id': 'Area does not exist.'}},
                        status=status.HTTP_400_BAD_REQUEST)
                except IntegrityError:
                    return Response(
                        {'detail': 'Create new candidate failed', 'errors': {'user_id': 'User already a candidate.'}},
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
                    candidate = NewCandidate.objects.get(id=serializer.validated_data['candidate_id'])
                except NewCandidate.DoesNotExist:
                    return Response(
                        {'detail': 'Update candidate failed', 'errors': {'detail': 'Candidate does not exist.'}}
                        , status=status.HTTP_400_BAD_REQUEST)
                data_key_list = serializer.validated_data.keys()
                if 'user_id' in data_key_list:
                    try:
                        user = User.objects.get(id=serializer.validated_data['user_id'])
                        candidate.user = user
                    except User.DoesNotExist:
                        return Response(
                            {'detail': 'Update candidate failed', 'errors': {'user_id': 'User does not exist.'}}
                            , status=status.HTTP_400_BAD_REQUEST)
                if 'description' in data_key_list:
                    if serializer.validated_data['description'] != '':
                        candidate.description = serializer.validated_data['description']
                if 'area_id' in data_key_list:
                    if serializer.validated_data['area_id'] != '':
                        try:
                            area = NewArea.objects.get(id=serializer.validated_data['area_id'])
                            candidate.area = area
                        except NewArea.DoesNotExist:
                            return Response({'detail': 'Update candidate failed',
                                             'errors': {'area_id': 'Area does not exist.'}}
                                            , status=status.HTTP_400_BAD_REQUEST)
                try:
                    candidate.save()
                except IntegrityError:
                    return Response(
                        {'detail': 'Update candidate failed', 'errors': {'user_id': 'User already a candidate.'}},
                        status=status.HTTP_400_BAD_REQUEST)
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


class CandidateDetailView(views.APIView):
    permissions_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={
        200: serializers.GetCandidateSerializer,
        404: serializers.ErrorSerializer(detail='Candidate does not exist.')
    })
    def get(self, request, candidate_id):
        """
        Get a candidate detail.

        Get the full detail of the target candidate.
        """
        try:
            candidate = NewCandidate.objects.get(id=candidate_id)
            serializer = serializers.GetCandidateSerializer(candidate, context={'request': self.request})
            return Response({'detail': 'Get candidate detail successfully', 'candidate': serializer.data},
                            status=status.HTTP_200_OK)
        except NewCandidate.DoesNotExist:
            return Response(
                {'detail': 'Get candidate detail failed', 'errors': {'detail': 'Candidate does not exist.'}},
                status=status.HTTP_404_NOT_FOUND)


class ElectionsView(views.APIView):
    permissions_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: serializers.GetElectionSerializer(many=True)})
    def get(self, request):
        """
        Get all elections.

        Get a list of all elections.
        """
        serializer = serializers.GetElectionSerializer(NewElection.objects.all().order_by('id'), many=True,
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
            if serializer.is_valid() and not is_there_ongoing_election():
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
                    election = NewElection.objects.get(id=serializer.validated_data['election_id'])
                except NewElection.DoesNotExist:
                    return Response(
                        {'detail': 'Update election failed', 'errors': {'detail': 'Election does not exist.'}})
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


class ElectionCurrentView(views.APIView):
    permissions_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={
        200: serializers.GetElectionSerializer,
        404: serializers.ErrorSerializer(detail='Ongoing election does not exist.')
    })
    def get(self, request):
        """
        Get an only-one ongoing election.
        """
        try:
            election = NewElection.objects.get(start_date__gte=timezone.now(), end_date__lt=timezone.now())
            serializer = serializers.GetElectionSerializer(election, context={'request': self.request})
            return Response({'detail': 'Get ongoing election successfully', 'election': serializer.data},
                            status=status.HTTP_200_OK)
        except NewElection.DoesNotExist:
            return Response({'detail': 'Get ongoing election failed', 'errors': {'detail': 'There are no '
                                                                                           'ongoing '
                                                                                           'election.'}},
                            status=status.HTTP_404_NOT_FOUND)


class ElectionDetailView(views.APIView):
    permissions_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={
        200: serializers.GetElectionSerializer,
        404: serializers.ErrorSerializer(detail='Election does not exist.'),
        400: serializers.ErrorSerializer(detail='Invalid election info')
    })
    def get(self, request, election_id):
        """
        Get an election detail.

        Get the full detail of the target election.
        """
        try:
            election = NewElection.objects.get(id=election_id)
            serializer = serializers.GetElectionSerializer(election, context={'request': self.request})
            return Response({'detail': 'Get election detail successfully', 'election': serializer.data},
                            status=status.HTTP_200_OK)
        except NewElection.DoesNotExist:
            return Response({'detail': 'Get election detail failed', 'errors': {'detail': 'Election does not exist.'}},
                            status=status.HTTP_404_NOT_FOUND)


class ElectionVoteView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=serializers.VoteSerializer, responses={
        404: serializers.ErrorSerializer(detail='Election does not exist.'),
        201: serializers.VoteCheckSerializer
    })
    def post(self, request, election_id):
        """
        Vote candidate and party in the election

        Post the vote using given `candidate_id` and `party_id`
        """
        vote_data = VoteSerializer(data=request.data)
        if not vote_data.is_valid():
            return Response({'detail': 'Vote failed', 'errors': vote_data.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            election = NewElection.objects.get(id=election_id)
            if VoteCheck.objects.filter(user=request.user, election=election).exists():
                return Response({'detail': 'Vote failed', 'errors': {'detail': 'Already voted'}},
                                status=status.HTTP_400_BAD_REQUEST)

            if timezone.now() > election.end_date:
                return Response({'detail': 'Vote failed', 'errors': {'detail': 'Election is already ended.'}},
                                status=status.HTTP_400_BAD_REQUEST)
            if timezone.now() < election.start_date:
                return Response({'detail': 'Vote failed', 'errors': {'detail': 'Election is not open yet.'}},
                                status=status.HTTP_400_BAD_REQUEST)

            # TODO: Area check

            candidate_id = vote_data.data['candidate_id']

            if not NewCandidate.objects.filter(id=candidate_id).exists():
                return Response({'detail': 'Vote failed', 'errors': {'detail': 'Candidate does not exist.'}},
                                status=status.HTTP_400_BAD_REQUEST)

            if request.user.newprofile.area is None:
                return Response({'detail': 'Vote failed',
                                 'errors': {'detail': 'Please contact administrator to set area.'}},
                                status=status.HTTP_400_BAD_REQUEST)

            if NewCandidate.objects.get(id=candidate_id).area.id != request.user.newprofile.area.id:
                return Response({'detail': 'Vote failed', 'errors': {'detail': 'Cannot vote candidate outside area'}},
                                status=status.HTTP_400_BAD_REQUEST)

            party_id = vote_data.data['party_id']
            if not NewParty.objects.filter(id=party_id).exists():
                return Response({'detail': 'Vote failed', 'errors': {'detail': 'Party does not exist.'}},
                                status=status.HTTP_400_BAD_REQUEST)

            vote_result_candidate, _ = VoteResultCandidate.objects.get_or_create(election=election,
                                                                                 candidate_id=candidate_id)
            vote_result_candidate.vote += 1
            vote_result_candidate.save()
            vote_result_party, _ = VoteResultParty.objects.get_or_create(election=election,
                                                                         party_id=party_id)
            vote_result_party.vote += 1
            vote_result_party.save()
            vote_check = VoteCheck.objects.create(election=election, user=request.user)

            # Success
            return Response({'detail': 'Vote successfully', 'vote_check': VoteCheckSerializer(vote_check).data},
                            status=status.HTTP_201_CREATED)

        except NewElection.DoesNotExist:
            return Response({'detail': 'Vote failed', 'errors': {'detail': 'Election does not exist.'}})


class PartyView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={
        200: serializers.PartySerializer(many=True)
    })
    def get(self, request):
        """
        Get all party list.

        Get the list of all party.
        """
        party = NewParty.objects.all().order_by('id')
        serializer = serializers.PartySerializer(data=party, many=True, context={'request': self.request})
        serializer.is_valid()
        return Response({'detail': 'Get party list successfully', 'party': serializer.data},
                        status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=serializers.PartySerializer, responses={
        201: serializers.PartySerializer,
        401: serializers.ErrorSerializer(detail="You do not have permission to perform this action."),
        400: serializers.PartySerializer
    })
    def post(self, request):
        """
        Create an empty party without candidate (Currently does not support upload image)

        Create an empty party without candidate. Candidate can be assigned later.
        """
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            return Response({'detail': 'Create new party failed',
                             'errors': {'detail': 'You do not have permission to perform this action.'}},
                            status=status.HTTP_401_UNAUTHORIZED)
        serializer = serializers.PartySerializer(data=request.data, context={'request': self.request})
        if not serializer.is_valid():
            return Response({'detail': 'Create new party failed', 'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'detail': 'Create new party successfully',
                         'result': serializers.PartySerializer(serializer.instance, context={
                             'request': self.request}).data}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=serializers.PartySerializer, responses={
        200: serializers.PartySerializer,
        401: serializers.ErrorSerializer(detail="You do not have permission to perform this action."),
        400: serializers.PartySerializer
    })
    def put(self, request):
        """
        Update party (Currently does not support upload image)

        Update party from given input. This action can be done by staff only.
        """
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            return Response({'detail': 'Edit party failed',
                             'errors': {'detail': 'You do not have permission to perform this action.'}},
                            status=status.HTTP_401_UNAUTHORIZED)
        serializer = serializers.PartySerializer(request.data)
        if not serializer.is_valid():
            return Response({'detail': 'Edit party failed', 'errors': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            party = NewParty.objects.get(id=serializer.validated_data['id'])
        except NewParty.DoesNotExist:
            return Response(
                {
                    'detail': 'Update party failed',
                    'errors': {
                        'detail': 'Party does not exist.'
                    }
                }
            )
        data_key_list = serializer.validated_data.keys()
        validated_data = serializer.validated_data
        if 'description' in data_key_list and validated_data['description'] != '':
            party.description = validated_data['description']
        if 'name' in data_key_list and validated_data['name'] != '':
            party.name = validated_data['name']
        # No support for uploading image yet
        party.save()
        return Response({
            'detail': 'Update party successfully',
            'result': serializers.PartySerializer(party, context={
                'request': self.request}).data}, status=status.HTTP_201_CREATED)


class PartyDetailView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={
        200: serializers.PartyWithCandidateSerializer,
        404: serializers.ErrorSerializer(detail='Party does not exist.')
    })
    def get(self, request, party_id):
        """
        Get a party detail.

        Get the full detail of the target party.
        """
        try:
            party = NewParty.objects.get(id=party_id)
            serializer = serializers.PartyWithCandidateSerializer(party, context={'request': self.request})
            return Response({'detail': 'Get party detail successfully', 'party': serializer.data},
                            status=status.HTTP_200_OK)
        except NewParty.DoesNotExist:
            return Response({'detail': 'Get party detail failed', 'errors': {'detail': 'Party does not exist.'}},
                            status=status.HTTP_404_NOT_FOUND)


class ElectionResultByAreaView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={
        200: serializers.VoteAreaResultSerializer,
        404: serializers.ErrorSerializer(detail='Election does not exist.'),
        400: serializers.ErrorSerializer(detail='Election has not ended.')
    })
    def get(self, request, election_id, area_id):
        """
        Get an election result by area.

        Get the result of candidate vote in the target area sort by vote count.
        """
        try:
            election = NewElection.objects.get(id=election_id)
        except NewElection.DoesNotExist:
            return Response({'detail': 'Get election result failed', 'errors': {'detail': 'Election does not exist.'}},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            area = NewArea.objects.get(id=area_id)
        except NewArea.DoesNotExist:
            return Response({'detail': 'Get election result failed', 'errors': {'detail': 'Area does not exist.'}},
                            status=status.HTTP_404_NOT_FOUND)
        if check_election_status(election) != 'Finished' and (
                request.user.is_staff or request.user.is_superuser) or check_election_status(
            election) == 'Finished':
            vote_result = VoteResultCandidate.objects.filter(election=election, candidate__area_id=area_id).order_by(
                '-vote')
            candidate_no_vote = []
            candidate_in_area = NewCandidate.objects.filter(area_id=area_id).order_by('id')
            for candidate in candidate_in_area:
                if not vote_result.filter(candidate=candidate):
                    candidate_no_vote.append(candidate)
            api_result = []
            for result in vote_result:
                # Set candidate and vote in VoteAreaResultSerializer
                api_result.append({'candidate': result.candidate, 'vote_count': result.vote})
            for candidate in candidate_no_vote:
                api_result.append({'candidate': candidate, 'vote_count': 0})
            return Response({'detail': 'Get election result successfully',
                             'vote_result': serializers.VoteAreaResultSerializer(api_result, many=True, context={
                                 'request': self.request}).data})
        else:
            return Response(
                {'detail': 'Get election result failed', 'errors': {'detail': 'Election has not finished.'}},
                status=status.HTTP_400_BAD_REQUEST)


class RawElectionResultByPartyView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={
        200: serializers.VotePartyRawResultSerializer,
        404: serializers.ErrorSerializer(detail='Election does not exist.'),
        400: serializers.ErrorSerializer(detail='Election has not ended.')
    })
    def get(self, request, election_id):
        """
        Get a raw election result by party.

        Get the raw result of party vote sorted by vote count.
        """
        try:
            election = NewElection.objects.get(id=election_id)
        except NewElection.DoesNotExist:
            return Response({'detail': 'Get election result failed', 'errors': {'detail': 'Election does not exist.'}},
                            status=status.HTTP_404_NOT_FOUND)
        if check_election_status(election) != 'Finished' and (
                request.user.is_staff or request.user.is_superuser) or check_election_status(election) == 'Finished':
            vote_result = VoteResultParty.objects.filter(election=election).order_by('-vote')
            party_no_vote = []
            for party in NewParty.objects.all():
                if not vote_result.filter(party=party):
                    party_no_vote.append(party)
            api_result = []
            for result in vote_result:
                # Set candidate and vote in VoteAreaResultSerializer
                api_result.append({'party': result.party, 'vote_count': result.vote})
            for party in party_no_vote:
                api_result.append({'party': party, 'vote_count': 0})
            return Response({'detail': 'Get election result successfully',
                             'vote_result': serializers.VotePartyRawResultSerializer(api_result, many=True, context={
                                 'request': self.request}).data})
        else:
            return Response(
                {'detail': 'Get election result failed', 'errors': {'detail': 'Election has not finished.'}},
                status=status.HTTP_400_BAD_REQUEST)


class ElectionResultByPartyView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={
        200: serializers.PartylistElectionResultSerializer,
        404: serializers.ErrorSerializer(detail='Election does not exist.'),
        400: serializers.ErrorSerializer(detail='Election has not ended.')
    })
    def get(self, request, election_id):
        """
        Get a calculated election result by party.

        Get the calculated result or partylist of the election
        """
        try:
            election = NewElection.objects.get(id=election_id)
        except NewElection.DoesNotExist:
            return Response({'detail': 'Get election result failed', 'errors': {'detail': 'Election does not exist.'}},
                            status=status.HTTP_404_NOT_FOUND)
        if check_election_status(election) != 'Finished' and (
                request.user.is_staff or request.user.is_superuser) or check_election_status(election) == 'Finished':
            result = calculate_election_party_result(election.id)
            result = result['result']
            api_result = []
            for data in result:
                api_result.append({
                    'party': data['party'],
                    'supposed_to_have_result': data['supposed_to_have'],
                    'real_result': data['real']
                })
            return Response({'detail': 'Get election result successfully',
                             'vote_result': serializers.PartylistElectionResultSerializer(api_result, many=True,
                                                                                          context={
                                                                                              'request': self.request}).data})
        else:
            return Response(
                {'detail': 'Get election result failed', 'errors': {'detail': 'Election has not finished.'}},
                status=status.HTTP_400_BAD_REQUEST)
