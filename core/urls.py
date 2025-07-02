from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
	path('', views.HomePage, name='home-page'),
    path('login/', views.LogIn, name='log-in'),
    path('dashboard/', views.Dashboard, name = 'dashboard'),
    path('profile/', views.ViewProfile, name = 'view-profile'),
    
    path('auth/register', views.RegisterUser.as_view(), name = 'register-user'),
	path('auth/login/', TokenObtainPairView.as_view(), name="obtain-token"),
	path('auth/login/refresh/', TokenRefreshView.as_view(), name="refresh-token"),
    path('auth/me', views.GetUser, name='get-user'),

    path('users/me', views.GetProfile, name='get-user-profile'),
    path('users/<str:id>', views.GetId, name = 'get-profile-by-id'),
    path('users/me/profile', views.UpdateProfile, name = 'update-user-profile'),

    path('requests/', views.SendRequest.as_view(), name = 'send-mentorship-request'),
    path('requests/sent/', views.GetMenteeRequests, name = 'get-mentee-requests'),
    path('requests/received', views.GetMentorRequests, name = 'get-mentor-requests'),
    path('requests/<str:id>', views.UpdateStatus, name = 'update-request-status'),

    path('sessions/', views.ScheduleSession, name = 'schedule-session'),
    path('sessions/mentee', views.GetMenteeSessions, name = 'get-mentee-sessions'),
    path('sessions/mentor', views.GetMentorSessions, name = 'get-mentor-sessions'),
    path('sessions/<str:id>/feedback', views.SubmitFeedback, name = 'submit-feedback'),

    path('admin/users', views.ListAllUsers, name = 'list-all-users'),
    path('admin/users/<str:id>/role', views.UpdateUserRole, name = 'update-user-role'),

    path('notifications/delete', views.DeleteNotifications, name = 'delete-notifications')
]