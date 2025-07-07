from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Profile, MentorshipRequest, Mentorship, Session, Availability
from datetime import datetime, timedelta, time
from django.utils.timezone import make_aware
import json


class CoreAppTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.admin_user = User.objects.create_user(username="admin", email="admin@example.com", password="adminpass")
        self.mentor_user = User.objects.create_user(username="mentor", email="mentor@example.com", password="mentorpass")
        self.mentee_user = User.objects.create_user(username="mentee", email="mentee@example.com", password="menteepass")

        # Assign profiles
        Profile.objects.create(user=self.admin_user, role="admin")
        Profile.objects.create(user=self.mentor_user, role="mentor")
        Profile.objects.create(user=self.mentee_user, role="mentee")

        # Token login
        res = self.client.post("/auth/login/", {"username": "admin", "password": "adminpass"}, format="json")
        self.admin_token = res.data["access"]

        res = self.client.post("/auth/login/", {"username": "mentor", "password": "mentorpass"}, format="json")
        self.mentor_token = res.data["access"]

        res = self.client.post("/auth/login/", {"username": "mentee", "password": "menteepass"}, format="json")
        self.mentee_token = res.data["access"]

    def test_user_profile_retrieval(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.mentee_token}")
        res = self.client.get("/users/me")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["username"], "mentee")

    def test_send_mentorship_request(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.mentee_token}")
        res = self.client.post("/requests/", {"id": self.mentor_user.profile.id}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(MentorshipRequest.objects.count(), 1)

    def test_get_mentee_requests(self):
        MentorshipRequest.objects.create(mentee=self.mentee_user, mentor=self.mentor_user, status="pending")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.mentee_token}")
        res = self.client.get("/requests/sent/")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.data), 1)

    def test_get_mentor_requests(self):
        MentorshipRequest.objects.create(mentee=self.mentee_user, mentor=self.mentor_user, status="pending")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.mentor_token}")
        res = self.client.get("/requests/received")
        self.assertEqual(res.status_code, 200)
        self.assertIn("requests", res.data)

    def test_accept_mentorship_request(self):
        req = MentorshipRequest.objects.create(mentee=self.mentee_user, mentor=self.mentor_user, status="pending")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.mentor_token}")
        res = self.client.put(f"/requests/{req.id}", {"status": "accepted"}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Mentorship.objects.count(), 1)

    def test_schedule_session_within_availability(self):
        mentorship = Mentorship.objects.create(mentee=self.mentee_user, mentor=self.mentor_user)
        available_date = datetime.now().date()
        start_time = time(10, 0)
        end_time = time(12, 0)
        Availability.objects.create(mentor=self.mentor_user, date=available_date, start=start_time, end=end_time)

        requested_time = datetime.combine(available_date, time(11, 0)).isoformat()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.mentee_token}")
        res = self.client.post("/sessions/", {"id": mentorship.id, "date": requested_time}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Session.objects.count(), 1)

    def test_schedule_session_outside_availability(self):
        mentorship = Mentorship.objects.create(mentee=self.mentee_user, mentor=self.mentor_user)
        unavailable_date = datetime.now().date()
        Availability.objects.create(mentor=self.mentor_user, date=unavailable_date, start=time(10, 0), end=time(11, 0))

        requested_time = datetime.combine(unavailable_date, time(13, 0)).isoformat()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.mentee_token}")
        res = self.client.post("/sessions/", {"id": mentorship.id, "date": requested_time}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_submit_feedback(self):
        mentorship = Mentorship.objects.create(mentee=self.mentee_user, mentor=self.mentor_user)
        session = Session.objects.create(mentorship=mentorship, date=datetime.now().date())
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.mentee_token}")
        res = self.client.put(f"/sessions/{session.id}/feedback", {"feedback": "Very good", "rating": 5}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["feedback"], "Very good")

    def test_update_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.mentee_token}")
        res = self.client.put("/users/me/profile", {
            "bio": "Updated bio",
            "skills": "Python, Django",
            "goals": "Become senior dev"
        }, format="json")
        self.assertEqual(res.status_code, 200)
        profile = Profile.objects.get(user=self.mentee_user)
        self.assertEqual(profile.bio, "Updated bio")

    def test_list_all_users(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        res = self.client.get("/admin/allusers/")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(res.data), 3)

    def test_delete_notifications(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.mentee_token}")
        self.mentee_user.notifications.create(text="Test note")
        res = self.client.delete("/notifications/delete")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.mentee_user.notifications.count(), 0)
