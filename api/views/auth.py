from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth.models import User
from ..serializers import UserSerializer, PublicUserSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate email confirmation link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        confirm_url = request.build_absolute_uri(
            reverse('confirm-email', kwargs={'uidb64': uid, 'token': token})
        )

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



class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            if not user.is_active:
                return Response({'message': 'Bevestig eerst je e-mailadres.'}, status=403)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
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
        return Response({"message": "Je account is succesvol geactiveerd!"})
    else:
        return Response({"error": "Ongeldige of verlopen token."}, status=status.HTTP_400_BAD_REQUEST)