from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register('organism',OrganismViewSet, basename='organism')
router.register('quizzes', QuizViewSet, basename='quiz')  # Register QuizViewSet

customUrlPatters = [
    path("getQuizData/<int:quiz_id>/", get_quiz_data, name="get_quiz_data"),
]

urlpatterns = router.urls + customUrlPatters