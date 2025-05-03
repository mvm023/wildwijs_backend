from django.urls import path
from rest_framework.routers import DefaultRouter
from .views.quiz import *
from .views.auth import LoginView, UserRegistrationView, LogoutView, confirm_email

router = DefaultRouter()
router.register('organism',OrganismViewSet, basename='organism')
router.register('quizzes', QuizViewSet, basename='quiz')  # Register QuizViewSet

quizUrlPatterns = [
    path("getQuizData/<int:quiz_id>/", get_quiz_data, name="get_quiz_data"),
    path("startQuiz/<int:quiz_id>/", start_quiz, name="start_quiz"),
    path("answerQuestion/", answer_question, name="answer_question")
]

authenticationUrlPatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('confirm-email/<uidb64>/<token>/', confirm_email, name='confirm-email'),
]

urlpatterns = router.urls + quizUrlPatterns + authenticationUrlPatterns