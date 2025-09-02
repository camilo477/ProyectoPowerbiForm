from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from django.contrib.auth import get_user_model, authenticate, login
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse
import csv
from .serializers import CustomUserSerializer, CustomTokenObtainPairSerializer
from .models import NormalUserProfile  
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['GET'])
def session_view(request):
    email = request.query_params.get('email')
    if not email:
        return Response({"error": "Debe enviar un email"}, status=400)

    query = """
        SELECT u.id, u.email, u.username, u.is_superuser,
               p.form_link, p.powerbi_link
        FROM accounts_customuser u
        LEFT JOIN accounts_normaluserprofile p ON u.id = p.user_id
        WHERE u.email = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [email])
        row = cursor.fetchone()

    if row:
        user_data = {
            "id": row[0],
            "email": row[1],
            "username": row[2],
            "is_superuser": row[3],
            "form_link": row[4] or "",
            "powerbi_link": row[5] or ""
        }
        return Response({"success": True, **user_data})
    else:
        return Response({"error": "Usuario no encontrado"}, status=404)

User = get_user_model()

from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)  
            return Response({"success": True, "email": user.email, "is_superuser": user.is_superuser})
        return Response({"success": False, "error": "Credenciales inválidas"})

class SessionView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                "authenticated": True,
                "email": request.user.email,
                "username": request.user.username,
                "is_superuser": request.user.is_superuser
            })
        return Response({"authenticated": False})
class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_superuser": user.is_superuser
        })


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class ExportUsersCSV(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="usuarios.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Username', 'Email'])  # encabezados

        for user in User.objects.all():
            writer.writerow([user.id, user.username, user.email])

        return response


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]


class RegisterUserView(APIView):

    def post(self, request):

        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")
        form_link = request.data.get("form_link")
        powerbi_link = request.data.get("powerbi_link")

        if User.objects.filter(username=username).exists():
            return Response({"error": "Usuario ya existe"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        NormalUserProfile.objects.create(user=user, form_link=form_link, powerbi_link=powerbi_link)

        return Response({"message": "Usuario creado exitosamente"}, status=status.HTTP_201_CREATED)
