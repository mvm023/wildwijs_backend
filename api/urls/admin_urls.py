from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.admin_views import *

admin_router = DefaultRouter()
admin_router.register('quizcategory', QuizCategoryAdminViewSet, basename='admin-quizcategory')

adminUrlPatterns = [
    path('', include(admin_router.urls)),
]