from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework import serializers

from apps.models import Area, Candidate
from users.models import Profile


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
        model = Profile
        fields = ('image', 'area')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    This serializer is used to serialize the user profile model.
    """
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ('user', 'image', 'area')
        depth = 1


class AreaSerializer(serializers.ModelSerializer):
    """
    This serializer is used to serialize the area model.
    """
    class Meta:
        model = Area
        fields = ('id', 'name', 'description')


class CandidateSerializer(serializers.ModelSerializer):
    """
    This serializer is used to serialize the candidate model.
    This serializer need request context to get the website URL.
    """
    area = AreaSerializer()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = ('id', 'name', 'description', 'image', 'area')
        depth = 1

    def get_image(self, obj):
        """Add website URL to image path."""
        return self.context['request'].build_absolute_uri(obj.image.url)
