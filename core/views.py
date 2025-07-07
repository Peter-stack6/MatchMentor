from dateutil import parser as date_parser
from datetime import datetime

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import Response, APIView
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.status import HTTP_200_OK

from .serializers import *
from .models import Profile, Notification, MentorshipRequest, Mentorship, Session, Availability

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

@login_required(login_url = 'login/')
def EditProfile(request):
	return render(request, "editProfile.html")

@login_required(login_url = 'login/')
def AdminRegister(request):
	return render(request, "register.html")

@login_required(login_url = 'login/')
def Mentors(request):
	return render(request, "mentors.html")

@login_required(login_url = 'login/')
def MyRequests(request):
	return render(request, "my_requests.html")

@login_required(login_url = 'login/')
def MySessions(request):
	return render(request, "my_sessions.html")

@login_required(login_url = 'login/')
def availability(request):
	return render(request, "availability.html")

@login_required(login_url = 'login/') 
def mentor_requests(request):
	return render(request, "requests.html")

@login_required(login_url = 'login/') 
def mentor_sessions(request):
	return render(request, "mentor_sessions.html")

@login_required(login_url = 'login/') 
def matches(request):
	return render(request, "matches.html")

@login_required(login_url = 'login/') 
def sessions(request):
	return render(request, "sessions.html")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetUser(request):
	username = request.user.username
	role = request.user.profile.role
	return Response({'username': username, 'role': role}, status = status.HTTP_200_OK)

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
	profile = get_object_or_404(Profile, pk = id)

	serializer = ProfileSerializer(profile)
	return Response(serializer.data, status = status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def UpdateProfile(request):
	user = request.user

	data = JSONParser().parse(request)
	serializer = ProfileSerializer(data = data)

	if serializer.is_valid(raise_exception = True):
		details = serializer.data

		user_profile = user.profile
		user_profile.bio = details['bio']
		user_profile.skills = details['skills']
		user_profile.goals = details['goals']
		user_profile.save()

		Notification.objects.create(
			user = user,
			text = "You updated your profile"
		)
		return Response(serializer.data, status.HTTP_200_OK)

class RegisterUser(APIView):

	permission_classes = [IsAuthenticated, IsAdminUser]

	def post(self, request):

		data = JSONParser().parse(request)
		serializer = Register(data = data)
		
		if serializer.is_valid(raise_exception = True):
			user = serializer.save()

			Notification.objects.create(
				user = request.user,
				text = f"You added the user {user.username}"
			)

			return Response(serializer.data, status = status.HTTP_200_OK)

class SendRequest(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		mentee = request.user

		mentor_profile = get_object_or_404(Profile, pk = request.data.get("id"))
		mentor = mentor_profile.user

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

		return Response({"Success": "successful"}, status = status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetMenteeRequests(request):
	mentee = request.user

	all_requests = mentee.mentee_request.all()
	serializer = MentorshipReqSerializer(all_requests, many = True)

	return Response(serializer.data, status = HTTP_200_OK)

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
        mentorship_request = get_object_or_404(MentorshipRequest, pk=id)

        # Ensure only the assigned mentor can respond
        if mentorship_request.mentor != mentor:
            return Response(
                {"detail": "You are not authorized to update this request."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate input with StatusSerializer
        serializer = StatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        status_value = serializer.validated_data.get('status')
        mentee = mentorship_request.mentee

        if status_value == "accepted":
            Mentorship.objects.create(mentee=mentee, mentor=mentor)
            Notification.objects.create(
                user=mentee,
                text=f"The mentor {mentor.username} has accepted your mentorship request"
            )
            Notification.objects.create(
                user=mentor,
                text=f"You accepted the mentee {mentee.username}'s request"
            )

        elif status_value == "rejected":
            Notification.objects.create(
                user=mentee,
                text=f"The mentor {mentor.username} has rejected your mentorship request"
            )
            Notification.objects.create(
                user=mentor,
                text=f"You rejected the mentee {mentee.username}'s request"
            )

        # Delete the request regardless of status
        mentorship_request.delete()

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as error:
        return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ScheduleSession(request):
    """
    Schedule a mentorship session only if the requested datetime
    falls within the mentor's availability blocks.
    """
    try:
        data = JSONParser().parse(request)
        mentorship = get_object_or_404(Mentorship, pk=data.get('id'))
        requested_dt = date_parser.isoparse(data.get('date'))
    except Exception as e:
        return Response(
            {"detail": "Invalid payload or datetime format."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Fetch availability blocks for this mentor on that date
    avail_blocks = Availability.objects.filter(
        mentor=mentorship.mentor,
        date=requested_dt.date()
    )

    # Check if requested datetime fits in any block
    for block in avail_blocks:
        start_dt = datetime.combine(block.date, block.start)
        end_dt   = datetime.combine(block.date, block.end)
        if start_dt <= requested_dt <= end_dt:
            # Good: within availability → create session
            session = Session.objects.create(
                mentorship=mentorship,
                date=data.get('date')
            )
            serializer = SessionSerializer(session)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # No matching block found → reject
    return Response(
        {"detail": "Requested time not within mentor's availability."},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetMenteeSessions(request):
		mentee = request.user
		sessions = Session.objects.filter(mentorship__mentee=mentee)

		serializer = SessionSerializer(sessions, many = True)
		return Response({"sessions": serializer.data}, status = status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetMentorSessions(request):
	try:
		mentor = request.user
		sessions = Session.objects.filter(mentorship__mentor=mentor)

		serializer = SessionSerializer(sessions, many = True)
		return Response({"sessions": serializer.data}, status = status.HTTP_200_OK)
	
	except Exception as error:
		return Response({"Error": str(error)}, status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_availability(request):
    user = request.user

    if not user.profile.role == "mentor":
        return Response({'detail': 'Only mentors can set availability.'}, status=403)

    data = request.data
    try:
        date_str = data.get('date')
        start_str = data.get('start')
        end_str = data.get('end')

        if not (date_str and start_str and end_str):
            raise ValueError("All fields required")

        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_str, '%H:%M').time()
        end_time = datetime.strptime(end_str, '%H:%M').time()

        if start_time >= end_time:
            return Response({'detail': 'Start time must be before end time.'}, status=400)

        # Save it
        Availability.objects.create(
            mentor=user,
            date=date_obj,
            start=start_time,
            end=end_time,
        )
        return Response({'detail': 'Availability block created.'}, status=200)

    except Exception as e:
        return Response({'detail': f'Invalid input. {str(e)}'}, status=400)

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

@api_view(['GET'])
# @permission_classes([IsAuthenticated, IsAdminUser])
def ListAllUsers(request):
	try:
		all_users = User.objects.all()
		serializer = UserSerializer(all_users, many = True)

		return Response(serializer.data, status = status.HTTP_200_OK)

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_mentorships(request):
    mentorships = Mentorship.objects.filter(mentee=request.user)

    # Optional: enrich the data with mentor username
    data = []
    for m in mentorships:
        data.append({
            'id': m.id,
            'mentor': m.mentor.id,
            'mentor_username': m.mentor.username,
        })

    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def ManualMatch(request):
	mentee_id = request.data.get('mentee_id')
	mentor_id = request.data.get('mentor_id')

	mentee_profile = get_object_or_404(Profile, pk = mentee_id)
	mentor_profile = get_object_or_404(Profile, pk = mentor_id)

	mentee = mentee_profile.user
	mentor = mentor_profile.user

	Mentorship.objects.create(
		mentee = mentee,
		mentor = mentor
	)

	Notification.objects.create(
		user = mentee,
		text = f"The admin user {request.user.username} matched you with the mentor {mentor.username}"
	)

	Notification.objects.create(
		user = mentor,
		text = f"The admin user {request.user.username} matched you with {mentee.username}"
	)

	Notification.objects.create(
		user = request.user,
		text = f"You mathced the mentee {mentee.username} with the mentor {mentor.username}"
	)

	return Response({"details": "Sucessfully matched"}, status = HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def GetAllSessions(request):
	all_sessions = Session.objects.all()
	serializer = SessionSerializer(all_sessions, many = True)

	return Response(serializer.data, status = HTTP_200_OK)