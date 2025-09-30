from django.urls import path
from .views import (
    LoginView,
    SessionView,
    RegisterUserView,
    ExportUsersCSV,
    UserListView,
    UserDetailView,
    MyProfileView,
    user_links,
)
from rest_framework_simplejwt.views import TokenRefreshView
from .views import session_view

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),               
    path("session/", SessionView.as_view(), name="session"),          
    path("register/", RegisterUserView.as_view(), name="register"),    
    path("users/", UserListView.as_view(), name="user_list"),          
    path("users/<int:pk>/", UserDetailView.as_view(), name="user_detail"), 
    path("me/", MyProfileView.as_view(), name="my_profile"),           
    path("export/csv/", ExportUsersCSV.as_view(), name="export_users_csv"), 
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"), 
    path('powerbi-link/', session_view, name='powerbi-link'),
    path("user-links/", user_links, name="user-links"),
]


