from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import Response, APIView
from rest_framework.parsers import JSONParser
from rest_framework import status

from .serializers import *
from .models import Profile, Notification, MentorshipRequest, Mentorship, Session

def HomePage(request):
	return render(request, "index.html")

def LogIn(request):
	return render(request, "login.html")

@login_required(login_url = 'login/')
def Dashboard(request):
	return render(request, "dashboard.html")

@login_required(login_url = 'login/')
def ViewProfile(request):
	return render(request, "viewProfile.html")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetUser(request):
	username = request.user.username
	return Response({'username': username}, status = status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetProfile(request):
	user = request.user
	username = user.username

	profile = user.profile
	role = profile.role
	bio = profile.bio
	skills = profile.skills
	goals = profile.goals

	notifications = user.notifications.all()
	serializer = NotificationParser(notifications, many = True)

	return Response({'username': username, 'role': role, 'bio': bio, 'skills': skills, 'goals': goals, 'notifications': serializer.data}, status = status.HTTP_200_OK)

@api_view(['GET'])
def GetId(request, id):
	user = get_object_or_404(User, pk = id)
	profile = user.profile

	serializer = ProfileSerializer(profile, many = True)
	return Response({'profile': serializer.data})

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def UpdateProfile(request):
	user = request.user

	try:
		data = JSONParser().parse(request)
		serializer = ProfileSerializer(data = data)

		if serializer.is_valid(raise_exception = True):
			details = serializer.data

			user_profile = user.profile
			user_profile.bio = details.bio
			user_profile.skills = details.skills
			user_profile.goals = details.goals
			user_profile.save()

			Notification.objects.create(
				user = user,
				text = "You updated your profile"
			)


	except Exception as e:
		pass

class RegisterUser(APIView):

	# permission_classes = [IsAuthenticated, IsAdminUser]

	def post(self, request):

		try:
			data = JSONParser().parse(request)
			serializer = Register(data = data)
			
			if serializer.is_valid(raise_exception = True):
				user = serializer.save()
				role = serializer.data.role

				Profile.objects.create(
					user = user,
					role = role
				)

				Notification.objects.create(
					user = user,
					text = "The admin user has added your user"
				)

				if role == "admin":
					user.is_superuser = True

				return Response(serializer.data, status = status.HTTP_200_OK)
			
		except Exception as error:
			return Response({"Error": str(error)}, status = status.HTTP_400_BAD_REQUEST)

class SendRequest(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		try:

			data = JSONParser().parse(request)
			serializer = UserSerializer(data = data, partial = True)

			mentee = request.user
			mentor = get_object_or_404(User, pk = serializer.data.id)

			MentorshipRequest.objects.create(
				mentee = mentee,
				mentor = mentor,
				status = 'pending'
			)

			Notification.objects.create(
				user = request.user,
				text = f"You sent a mentorship request to the mentor {mentor.username}"
			)

			Notification.objects.create(
				user = mentor,
				text = f"You received a mentorship request from {request.user.username}"
			)

			return Response({"Success": "successful"}, status = HTTP_200_OK)

		except Exception as error:
			return Response({"Error": str(error)}, status = status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetMenteeRequests(request):
	mentee = request.user

	all_requests = mentee.mentee_request.all()
	serializer = MentorshipReqSerializer(all_requests, many = True)

	return Response({"requests": serializer.data}, status = HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetMentorRequests(request):
	mentor = request.user

	all_requests = mentor.mentor_request.all()
	serializer = MentorshipReqSerializer(all_requests, many = True)

	return Response({"requests": serializer.data}, status = HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def UpdateStatus(request, id):
	try:
		mentor = request.user
		mentorship_request = get_object_or_404(MentorshipRequest, pk = id)
		mentee = mentorship_request.mentee

		data = JSONParser().parse(request)
		serializer = StatusSerializer(data = data)

		if serializer.data.status == "accepted":
			Mentorship.objects.create(
				mentee = mentee,
				mentor = mentor
			)
			Notification.objects.create(
				user = mentee,
				text = f"The mentor {mentor.username} has accepted your mentorship request"
			)
			Notification.objects.create(
				user = mentor,
				text = f"You accepted the mentee {mentee.username}'s request"
			)
			mentorship_request.delete()
			return Response(serializer.data, status = HTTP_200_OK)

		elif serializer.data.status == "rejected":
			Notification.objects.create(
				user = mentee,
				text = f"The mentor {mentor.username} has rejected your mentorship request"
			)
			Notification.objects.create(
				user = mentor,
				text = f"You rejected the mentee {mentee.username}'s request"
			)
			mentorship_request.delete()

			return Response(serializer.data, status = HTTP_200_OK)
	except Exception as error:
		return Response({"Error": str(error)}, status = HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ScheduleSession(request):
	try:
		data = JSONParser().parse(request)
		serializer = SessionSerializer(data = data)

		mentorship = get_object_or_404(Mentorship, pk = serializer.data.id)

		Session.objects.create(
			mentorship = mentorship,
			date = serializer.data.date
		)

		Notification.objects.create(
			user = request.user,
			text = f"You scheduled a session with {mentorship.mentor}"
		)

		Notification.objects.create(
			user = mentorship.mentor,
			text = f"{request.user.username} scheduled a session with you"
		)

		return Response({serializer.data}, status = status.HTTP_200_OK)

	except Exception as error:
		return Response({"Error": str(error)}, status = status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetMenteeSessions(request):
	try:
		mentee = request.user
		mentorship = mentee.mentors.sessions.all()

		serializer = SessionSerializer(mentorship, many = True)
		return Response({"sessions": serializer.data}, status = status.HTTP_200_OK)

	except Exception as error:
		return Response({"Error": str(error)}, status = status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetMentorSessions(request):
	try:
		mentor = request.user
		sessions = mentor.mentees.sessions.all()

		serializer = SessionSerializer(sessions, many = True)
		return Response({"sessions": serializer.data}, status = status.HTTP_200_OK)
	
	except Exception as error:
		return Response({"Error": str(error)}, status = status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def SubmitFeedback(request, id):
	try:
		mentee = request.user
		session = get_object_or_404(Session, pk = id)

		data = JSONParser().parse(request)
		serializer = SessionSerializer(data = data, partial = True)

		if serializer.is_valid(raise_exception = True):
			serializer.save()
			return Response(serializer.data, status = status.HTTP_200_OK)
	except Exception as error:
		return Response({"Error": str(error)}, status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def ListAllUsers(request):
	try:
		all_users = User.objects.all()
		serializer = UserSerializer(all_users, many = True)

		return Response({"users": serializer.data}, status = HTTP_200_OK)

	except Exception as error:
		return Response({"Error": str(error)}, status = status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def UpdateUserRole(request, id):
	try:
		user = get_object_or_404(User, pk = id)
		data = JSONParser().parse(request)
		serializer = UserSerializer(data, partial = True)
		profile = user.profile

		profile.role = serializer.data.role
		return Response(serializer.data, status = status.HTTP_200_OK)
	except Exception as error:
		return Response({"Error": str(error)}, status = status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def DeleteNotifications(request):
	try:
		user = request.user
		user.notifications.all().delete()

		return Response({"done": "successfully deleted all"}, status = status.HTTP_200_OK)
	except Exception as error:
		return Response({"Error": str(error)}, status = status.HTTP_400_BAD_REQUEST)
