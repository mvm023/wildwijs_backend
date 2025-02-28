from django.urls import path
from .views import get_animal_data

urlpatterns = [
    path("getAnimalData/<str:animal_class>/<str:occurrence_status_type>/<str:max_length>/", get_animal_data, name="get_animal_data"),
]
