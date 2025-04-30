from django.urls import path
from rest_framework.routers import DefaultRouter
from .views.views import *
from .views.auth import LoginView, UserRegistrationView, LogoutView

router = DefaultRouter()
router.register('organism',OrganismViewSet, basename='organism')
router.register('quizzes', QuizViewSet, basename='quiz')  # Register QuizViewSet

quizUrlPatterns = [
    path("getQuizData/<int:quiz_id>/", get_quiz_data, name="get_quiz_data"),
]

authenticationUrlPatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

urlpatterns = router.urls + quizUrlPatterns + authenticationUrlPatterns