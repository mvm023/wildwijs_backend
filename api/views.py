import os
import random
import requests
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .serializers import *
from .models import *

# Using the MEDIA_URL and MEDIA_ROOT from settings
IMAGE_FOLDER = os.path.join(settings.MEDIA_ROOT, "images")

occurrence_status_codes = {
    "native": [
        "1a Oorspronkelijk. Minimaal 10 jaar achtereen voortplanting.",
        "1b Incidenteel/Periodiek. Minder dan 10 jaar achtereen voortplanting en toevallige gasten.",
    ],
    "invasive": [
        "2a Exoot. Minimaal 100 jaar zelfstandige handhaving.",
        "2b Exoot. Tussen 10 en 100 jaar zelfstandige handhaving.",
        "2c Exoot. Minder dan 10 jaar zelfstandige handhaving.",
        "2d Exoot. Incidentele import, geen voortplanting.",
    ],
}

occurrence_status_codes["both"] = occurrence_status_codes["native"] + occurrence_status_codes["invasive"]

birds_or_prey_orders = ["Accipitriformes", "Falconiformes", "Strigiformes"]


def fetch_animal_data(animal_class, occurrence_status_type, max_length):
    # Base queryset filtered by class
    organisms = Organism.objects.filter(classification__class_name=animal_class)

    if occurrence_status_type in occurrence_status_codes:
        organisms = organisms.filter(occurrence_status_verbatim__in=occurrence_status_codes[occurrence_status_type])
    elif occurrence_status_type == "birdsOfPrey":
        organisms = organisms.filter(classification__order__in=birds_or_prey_orders)

    organisms = list(organisms)
    random.shuffle(organisms)

    animals = []
    k = 0
    while len(animals) < max_length and k < len(organisms):
        organism = organisms[k]
        k += 1

        correct_name = organism.name

        # Construct image path
        image_filename = f"{animal_class}/{correct_name.lower().replace(' ', '_')}.jpg"
        image_url = f"{settings.MEDIA_URL}images/{image_filename}"

        animal_class_name = organism.classification.class_name
        animal_order = organism.classification.order
        animal_family = organism.classification.family

        # Prepare wrong answers based on database instead of API results
        wrong_answers = get_wrong_answers(animal_class_name, animal_order, animal_family, correct_name)

        animal = {
            "name": correct_name,
            "class": animal_class_name,
            "order": animal_order,
            "family": animal_family,
            "image": image_url,
            "wrongAnswers": wrong_answers,
        }
        if not any(a["name"] == correct_name for a in animals):
            print(f"Adding {animal['name']} to list of animals")
            animals.append(animal)

    return animals


def get_animal_data(request, animal_class, occurrence_status_type, max_length):
    """ API endpoint to get animal data for a given class (e.g., Aves, Mammalia). """
    animals = fetch_animal_data(animal_class, occurrence_status_type, int(max_length))
    return JsonResponse(animals, safe=False)


def get_wrong_answers(class_name, order, family, correct_name):
    """ Get wrong answers from the database. """

    # Try to find wrong answers first from the same family
    wrongs = Organism.objects.filter(
        classification__class_name=class_name,
        classification__order=order,
        classification__family=family
    ).exclude(name=correct_name)

    if wrongs.count() < 3:
        # Try from same order
        wrongs = Organism.objects.filter(
            classification__class_name=class_name,
            classification__order=order
        ).exclude(name=correct_name)

    if wrongs.count() < 3:
        # Try from same class
        wrongs = Organism.objects.filter(
            classification__class_name=class_name
        ).exclude(name=correct_name)

    wrong_names = list(wrongs.values_list('name', flat=True))
    wrong_names = list(set(wrong_names))  # Remove any duplicates

    while len(wrong_names) < 3:
        # Backup: randomly add names if too few
        extra = Organism.objects.exclude(name=correct_name).order_by('?').values_list('name', flat=True)[:1]
        if extra:
            wrong_names.append(extra[0])

    random.shuffle(wrong_names)
    return wrong_names[:3]


class organismViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Organism.objects.all()
    serializer_class = OrganismSerializer

    def list(self, request):
        queryset = Organism.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)