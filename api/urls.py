from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.quiz import *
from .views.auth import *
from knox import views as knox_views

router = DefaultRouter()
router.register('organism',OrganismViewSet, basename='organism')
router.register('quizzes', QuizViewSet, basename='quiz')
router.register('register', RegisterViewSet, basename='register')
router.register('login', LoginViewSet, basename='login')

quizUrlPatterns = [
    path("getQuizData/<int:quiz_id>/", get_quiz_data, name="get_quiz_data"),
    path("startQuiz/<int:quiz_id>/", start_quiz, name="start_quiz"),
    path("answerQuestion/", answer_question, name="answer_question"),
    path("endQuiz/<int:quiz_id>/", end_quiz, name="end_quiz"),
]

authenticationUrlPatterns = [
    path('confirm-email/<uidb64>/<token>/', confirm_email, name='confirm-email'),
    path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
    path('whoami/', whoami),
]

urlpatterns = router.urls + quizUrlPatterns + authenticationUrlPatterns