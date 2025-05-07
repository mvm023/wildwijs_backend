from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from ..serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth import logout
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import ensure_csrf_cookie
from knox.models import AuthToken

import os

FRONTEND_URL = 'https://wildwijs.nl' if 'RENDER_EXTERNAL_HOSTNAME' in os.environ else 'https://localhost:5173'


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out successfully."})

    
@api_view(['GET'])
def confirm_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        return Response({"error": "Ongeldige bevestigingslink."}, status=status.HTTP_400_BAD_REQUEST)

    if user.is_active:
        return Response({"message": "Account is al geactiveerd."})

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return Response({"message": "Je account is succesvol geactiveerd! Je kunt nu inloggen."})
    else:
        return Response({"error": "Ongeldige of verlopen token."}, status=status.HTTP_400_BAD_REQUEST)
    
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def whoami(request):
    if request.user.is_authenticated:
        data = {
            "username": request.user.username,
            "email": request.user.email,
        }
        if request.user.is_superuser:
            data["is_admin"] = True
        return Response(data)
    else:
        return Response({"username": None})


class RegisterViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate email confirmation link
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            confirm_url = f"{FRONTEND_URL}/activate-account/{uid}/{token}"

            # Send the email
            send_mail(
                subject='Bevestig je e-mailadres',
                message=f'Klik op de volgende link om je account te activeren: {confirm_url}',
                from_email='noreply@wildwijs.nl',
                recipient_list=[user.email],
            )

            return Response(
                {"message": "Gebruiker aangemaakt. Controleer je e-mail om je account te activeren."},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=400)
            

class LoginViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def create(self, request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)

            if user:
                _, token=AuthToken.objects.create(user)
                return Response(
                    {
                        "user": self.serializer_class(user).data,
                        "token": token
                    }
                )
            else:
                return Response({"error": "Invalid credentials"}, status=401)
        else:
            return Response(serializer.errors, status=400)