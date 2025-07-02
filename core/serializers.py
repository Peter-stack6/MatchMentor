from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notification, Profile, MentorshipRequest, Session

class Register(serializers.ModelSerializer):
    role = serializers.CharField(max_length = 6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

class NotificationParser(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'text', 'seen', 'date']

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['bio', 'skills', 'goals']

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source = 'profile.role', read_only = True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']
    
class MentorshipReqSerializer(serializers.ModelSerializer):
    mentee_name = serializers.CharField(source = 'mentee.username', read_only = True)
    mentor_name = serializers.CharField(source = 'mentor.username', read_only = True)

    class Meta:
        model = MentorshipRequest
        fields = [
            'mentee_name', 'mentor_name', 'mentee', 'mentor', 'status', 'created_at'
        ]

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorshipRequest
        fields = ['status']

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['mentorship', 'date', 'feedback', 'rating']