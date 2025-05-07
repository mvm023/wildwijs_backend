from rest_framework import viewsets
from ..biodiversity_api import *
from ..image_scrape_api import *
from ..serializers.admin_serializers import *
from ..permissions import *
from knox.auth import TokenAuthentication
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt


class QuizCategoryAdminViewSet(viewsets.ModelViewSet):
    queryset = QuizCategory.objects.all()
    serializer_class = QuizCategoryAdminSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

class QuizSubcategoryAdminViewSet(viewsets.ModelViewSet):
    queryset = QuizSubcategory.objects.all()
    serializer_class = QuizSubcategoryAdminSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [isAdminForAllMethods]

class QuizLayerAdminViewSet(viewsets.ModelViewSet):
    queryset = QuizLayer.objects.all()
    serializer_class = QuizLayerAdminSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [isAdminForAllMethods]

class QuizAdminViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizAdminSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [isAdminForAllMethods]


