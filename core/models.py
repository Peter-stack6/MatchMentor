from django.db import models
from django.contrib.auth.models import User
from cuid2 import Cuid

class Profile(models.Model):
    id = models.CharField(
            primary_key = True,
            max_length = 255,
            default = Cuid,
            editable = False
        )
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'profile')
    roles = [
        ('admin', 'Admin'),
        ('mentor', 'Mentor'),
        ('mentee', 'Mentee')
    ]
    role = models.CharField(max_length=6, choices=roles, default='mentee')

    bio = models.TextField(blank = True)
    skills = models.TextField(blank = True)
    goals = models.TextField(blank = True)


class Availability(models.Model):
    id = models.CharField(
            primary_key = True,
            max_length = 255,
            default = Cuid,
            editable = False
        )
    mentor = models.ForeignKey(
            User, on_delete = models.CASCADE, related_name = 'availability'
        )
    date = models.DateField()
    start = models.TimeField()
    end = models.TimeField()

class MentorshipRequest(models.Model):
    id = models.CharField(
        primary_key = True,
        max_length = 255,
        default = Cuid,
        editable = False
    )
    mentee = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'mentee_request')
    mentor = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'mentor_request')

    status_choices = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]
    status = models.CharField(max_length = 8, choices = status_choices)
    created_at = models.DateTimeField(auto_now = True)

class Mentorship(models.Model):
    mentee = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'mentors')
    mentor = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'mentees')
    created_at = models.DateTimeField(auto_now = True)

class Session(models.Model):
    id = models.CharField(
        primary_key = True,
        max_length = 255,
        default = Cuid,
        editable = False
    )
    mentorship = models.ForeignKey(Mentorship, on_delete = models.SET_NULL, null = True, blank = True, related_name = 'sessions')
    date = models.DateField()
    feedback = models.TextField(null = True, blank = True)
    rating = models.PositiveIntegerField(null = True, blank = True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'notifications')
    text = models.CharField(max_length = 255)
    seen = models.BooleanField(default = False)
    date = models.DateTimeField(auto_now = True)
    