from django.urls import path
from ..views.admin_views import *



adminUrlPatterns = [
    # For the list of quiz categories and the creation of a new category
    path('quizCategory/', QuizCategoryAdminAPIView.as_view(), name='quiz-category-list'),

    # For retrieving, updating, partially updating, or deleting a specific quiz category by its ID
    path('quizCategory/<int:pk>/', QuizCategoryAdminAPIView.as_view(), name='quiz-category-detail'),

        # For the list of quiz categories and the creation of a new category
    path('quizSubcategory/', QuizSubcategoryAdminAPIView.as_view(), name='quiz-category-list'),

    # For retrieving, updating, partially updating, or deleting a specific quiz category by its ID
    path('quizSubcategory/<int:pk>/', QuizSubcategoryAdminAPIView.as_view(), name='quiz-category-detail'),
]
