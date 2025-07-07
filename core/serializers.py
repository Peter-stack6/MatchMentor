from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notification, Profile, MentorshipRequest, Session

class Register(serializers.ModelSerializer):
    # Define role as a CharField
    role = serializers.CharField(max_length=6, write_only=True) # Make it write_only=True

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        role_data = validated_data.pop('role')


        user = User.objects.create_user(**validated_data)

        Profile.objects.create(
            user=user,
            role=role_data
        )

        # Create the Notification
        Notification.objects.create(
            user=user,
            text="The admin user has added your user"
        )

        # Set superuser status if admin
        if role_data == "admin":
            user.is_superuser = True
            user.save() # Save the user after modifying is_superuser

        return user # The create method must return the created model instance

class NotificationParser(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'text', 'seen', 'date']

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['id', 'bio', 'skills', 'goals']

class UserSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source = 'profile.id', read_only = True)
    role = serializers.CharField(source = 'profile.role', read_only = True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']
    
class MentorshipReqSerializer(serializers.ModelSerializer):
    mentee_profile_id = serializers.CharField(source = 'mentee.profile.id', read_only = True)
    mentee_name = serializers.CharField(source = 'mentee.username', read_only = True)
    mentor_name = serializers.CharField(source = 'mentor.username', read_only = True)

    class Meta:
        model = MentorshipRequest
        fields = [
            'id', 'mentee_profile_id', 'mentee_name', 'mentor_name', 'mentee', 'mentor', 'status', 'created_at'
        ]

class StatusSerializer(serializers.Serializer):
    class Meta:
        model = MentorshipRequest
        fields = ['status']

class SessionSerializer(serializers.ModelSerializer):
    mentee = serializers.CharField(source = 'mentorship.mentee.username', read_only = True)
    mentor = serializers.CharField(source = 'mentorship.mentor.username', read_only = True)

    class Meta:
        model = Session
        fields = ['mentee', 'mentor', 'mentorship', 'date', 'feedback', 'rating']