from rest_framework import viewsets
from ..biodiversity_api import *
from ..image_scrape_api import *
from ..serializers.admin_serializers import *
from ..permissions import *

class QuizCategoryAdminViewSet(viewsets.ModelViewSet):
    queryset = QuizCategory.objects.all()
    serializer_class = QuizCategoryAdminSerializer
    permission_classes = [isAdminForAllMethods]

