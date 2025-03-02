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
    """ Fetches animal data for a given class (e.g., Aves, Mammalia). """
    base_url = "https://api.biodiversitydata.nl/v2/taxon/query"
    query_params = {
        "defaultClassification.className": animal_class,
        "sourceSystem.code": "NSR",
        "_size": 1000,
        "_from": 0,
        "_fields": "vernacularNames,defaultClassification.className,defaultClassification.order,defaultClassification.family,occurrenceStatusVerbatim",
    }

    response = requests.get(base_url, params=query_params)
    if response.status_code != 200:
        return []

    data = response.json()
    results = data.get("resultSet", [])
    named_results = [i for i in results if "vernacularNames" in i["item"] and i["item"]["vernacularNames"]]

    if occurrence_status_type in occurrence_status_codes:
        filtered_results = [i for i in named_results if "occurrenceStatusVerbatim" in i["item"] and i["item"]["occurrenceStatusVerbatim"] in occurrence_status_codes[occurrence_status_type]]

    elif occurrence_status_type == "birdsOfPrey":
        filtered_results = [i for i in named_results if i["item"]["defaultClassification"]["order"] in birds_or_prey_orders]

    random.shuffle(filtered_results)

    animals = []
    k = 0
    while len(animals) < max_length and k < len(filtered_results):
        item = filtered_results[k]
        k += 1
        correct_name = item["item"]["vernacularNames"][0]["name"]

        # Construct image path
        image_filename = f"{animal_class}/{correct_name.lower().replace(' ', '_')}.jpg"
        image_url = f"{settings.MEDIA_URL}images/{image_filename}"
        image_path = os.path.join(IMAGE_FOLDER, image_filename)

        # Check if the image exists in the media folder
        if not os.path.exists(image_path):
            print(f"No image found for path {image_path}, skipping")
            continue  # Skip if no image found

        animal_class_name = item["item"]["defaultClassification"]["className"]
        animal_order = item["item"]["defaultClassification"]["order"]
        animal_family = item["item"]["defaultClassification"]["family"]

        animal = {
            "name": correct_name,
            "class": animal_class_name,
            "order": animal_order,
            "family": animal_family,
            "image": image_url,
            "wrongAnswers": get_wrong_answers(named_results, correct_name, order=animal_order, className=animal_class_name, family=animal_family),
        }
        if not any(a["name"] == correct_name for a in animals):
            print(f"Adding {animal['name']} to list of animals")
            animals.append(animal)
    return animals


def get_animal_data(request, animal_class, occurrence_status_type, max_length):
    """ API endpoint to get animal data for a given class (e.g., Aves, Mammalia). """
    animals = fetch_animal_data(animal_class, occurrence_status_type, int(max_length))
    return JsonResponse(animals, safe=False)


def get_wrong_answers(results, name, order, className, family):
    """ Fetch wrong answers for a given animal. """
    wrong_answers = [
        i["item"]["vernacularNames"][0]["name"]
        for i in results
        if i["item"]["vernacularNames"][0]["name"] != name
        and i["item"]["defaultClassification"]["className"] == className
        and i["item"]["defaultClassification"]["order"] == order
        and i["item"]["defaultClassification"]["family"] == family
    ]

    if len(wrong_answers) < 3:
        wrong_answers = [
            i["item"]["vernacularNames"][0]["name"]
            for i in results
            if i["item"]["vernacularNames"][0]["name"] != name
            and i["item"]["defaultClassification"]["className"] == className
            and i["item"]["defaultClassification"]["order"] == order
        ]

    if len(wrong_answers) < 3:
        wrong_answers = [
            i["item"]["vernacularNames"][0]["name"]
            for i in results
            if i["item"]["vernacularNames"][0]["name"] != name
            and i["item"]["defaultClassification"]["className"] == className
        ]

    wrong_answers = list(set(wrong_answers))

    while len(wrong_answers) < 3:
        new_item = random.choice(results)
        new_wrong_answer = new_item["item"]["vernacularNames"][0]["name"]
        if new_wrong_answer not in wrong_answers and new_wrong_answer != name:
            wrong_answers.append(new_wrong_answer)

    random.shuffle(wrong_answers)
    return wrong_answers[:3]

class organismViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Organism.objects.all()
    serializer_class = OrganismSerializer

    def list(self, request):
        queryset = Organism.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)