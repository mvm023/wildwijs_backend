from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register('organism',organismViewSet, basename='organism')

customUrlPatters = [
    path("getAnimalData/<str:animal_class>/<str:occurrence_status_type>/<str:max_length>/", get_animal_data, name="get_animal_data"),
]

urlpatterns = router.urls + customUrlPatters