from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from apps.models import NewArea, NewCandidate, NewElection, VoteCheck, \
    NewParty
from users.models import NewProfile


class LoginSerializer(serializers.Serializer):
    """
    This serializer defines two fields for authentication:
      * username
      * password.
    It will try to authenticate the user with when validated.
    """
    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        # This will be used when the DRF browsable API is enabled
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        # Take username and password from request
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Try to authenticate the user using Django auth framework.
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                # If we don't have a regular user, raise a ValidationError
                msg = 'Access denied: wrong username or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        # We have a valid user, put it in the serializer's validated_data.
        # It will be used in the view.
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    This serializer is used to serialize the user model.
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class ProfileSerializer(serializers.ModelSerializer):
    """
    This serializer is used to serialize the user profile model.
    """

    class Meta:
        model = NewProfile
        fields = ('image', 'area')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    This serializer is used to serialize the user profile model.
    """
    user = UserSerializer()
    image = serializers.SerializerMethodField()

    class Meta:
        model = NewProfile
        fields = ('user', 'image', 'area')
        depth = 1

    def get_image(self, obj):
        """Add website URL to image path."""
        return self.context['request'].build_absolute_uri(obj.image.url)


class PartySerializer(serializers.ModelSerializer):
    """
    This serializer is used to serialize the party model.
    """
    image = serializers.SerializerMethodField()

    class Meta:
        model = NewParty
        fields = ('id', 'name', 'description', 'image')

    def get_image(self, obj):
        """Add website URL to image path."""
        return self.context['request'].build_absolute_uri(obj.image.url)


class AreaSerializer(serializers.ModelSerializer):
    """
    This serializer is used to serialize the area model.
    """

    class Meta:
        model = NewArea
        fields = ('id', 'name', 'population', 'number_of_voters')


class UpdateAreaSerializer(serializers.ModelSerializer):
    """
    This serializer is used for updating the area model.
    """
    area_id = serializers.IntegerField(write_only=True)
    # Since we want user can only update some field, user can put blank value if they don't want to update.
    name = serializers.CharField(required=False, allow_blank=True)
    population = serializers.IntegerField(required=False)
    number_of_voters = serializers.IntegerField(required=False)

    class Meta:
        model = NewArea
        fields = ('area_id', 'name', 'population', 'number_of_voters')


class GetCandidateSerializer(serializers.ModelSerializer):
    """
    This serializer is used to serialize the candidate model.
    This serializer need request context to get the website URL.
    """
    area = AreaSerializer()
    user = UserSerializer()
    party = PartySerializer()
    image = serializers.SerializerMethodField()

    class Meta:
        model = NewCandidate
        fields = ('id', 'user', 'description', 'image', 'area', 'party')
        depth = 1

    def get_image(self, obj):
        """Add website URL to image path."""
        return self.context['request'].build_absolute_uri(obj.image.url)


class GetCandidateSerializerWithoutParty(serializers.ModelSerializer):
    """
    This serializer is used to serialize the candidate model.
    This serializer need request context to get the website URL.
    """
    area = AreaSerializer()
    user = UserSerializer()
    image = serializers.SerializerMethodField()

    class Meta:
        model = NewCandidate
        fields = ('id', 'user', 'description', 'image', 'area')
        depth = 1

    def get_image(self, obj):
        """Add website URL to image path."""
        return self.context['request'].build_absolute_uri(obj.image.url)


class CreateCandidateSerializer(serializers.ModelSerializer):
    """
    This serializer is used to serialize for creating a candidate.
    """
    # TODO: Support image upload
    user_id = serializers.IntegerField(write_only=True)
    area_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = NewCandidate
        fields = ('user_id', 'description', 'area_id')
        depth = 1


class UpdateCandidateSerializer(serializers.ModelSerializer):
    """
    This serializer is used for updating the candidate model.
    """
    candidate_id = serializers.IntegerField(write_only=True)
    # Since we want user can only update some field, user can put blank value if they don't want to update.
    user_id = serializers.IntegerField(required=False, write_only=True)
    description = serializers.CharField(required=False, allow_blank=True)
    area_id = serializers.IntegerField(required=False)

    class Meta:
        model = NewCandidate
        fields = ('candidate_id', 'user_id', 'description', 'area_id')
        depth = 1


class GetElectionSerializer(serializers.ModelSerializer):
    """
    This serializer is used to serialize the election model.
    This serializer need request context to get the website URL.
    """
    front_image = serializers.SerializerMethodField()

    class Meta:
        model = NewElection
        fields = ('id', 'name', 'description', 'start_date', 'end_date', 'front_image')

    def get_front_image(self, obj):
        """Add website URL to image path."""
        return self.context['request'].build_absolute_uri(obj.front_image.url)


class CreateElectionSerializer(serializers.ModelSerializer):
    """
    This serializer is used to serialize for creating an election.
    """

    class Meta:
        model = NewElection
        fields = ('name', 'description', 'start_date', 'end_date')


class UpdateElectionSerializer(serializers.ModelSerializer):
    """
    This serializer is used for updating the election model.
    """
    election_id = serializers.IntegerField(write_only=True)
    # Since we want user can only update some field, user can put blank value if they don't want to update.
    # For election model as in the edit election form, the system will only allow to make
    # some change on not essential information of the election only.
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = NewElection
        fields = ('election_id', 'description')


class ErrorSerializer(serializers.Serializer):
    """
    This serializer is used to serialize errors.
    """
    detail = serializers.CharField()

    def __init__(self, detail, *args, **kwargs):
        super(ErrorSerializer, self).__init__(*args, **kwargs)
        self.fields['detail'] = serializers.CharField(default=detail)


class VoteSerializer(serializers.Serializer):
    """
    This serializer is used for vote API request.
    """
    party_id = serializers.IntegerField()
    candidate_id = serializers.IntegerField()


class VoteCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteCheck
        fields = ('user_id', 'election_id')


class PartyWithCandidateSerializer(serializers.ModelSerializer):
    """
    This serializer is used to serialize the party model.
    """
    image = serializers.SerializerMethodField()
    candidates = serializers.SerializerMethodField()

    class Meta:
        model = NewParty
        fields = ('id', 'name', 'description', 'image', 'candidates')

    def get_image(self, obj):
        """Add website URL to image path."""
        return self.context['request'].build_absolute_uri(obj.image.url)

    def get_candidates(self, obj):
        candidates = NewCandidate.objects.filter(party=obj).order_by('id')
        return GetCandidateSerializerWithoutParty(candidates, many=True, context=self.context).data


class VoteAreaResultSerializer(serializers.Serializer):
    """
    This serializer is used to serialize the result of candidate vote in an area.
    """
    candidate = GetCandidateSerializer()
    vote_count = serializers.IntegerField()


class VotePartyRawResultSerializer(serializers.Serializer):
    """
    This serializer is used to serialize the raw result of party vote in an election.
    """
    party = PartySerializer()
    vote_count = serializers.IntegerField()

