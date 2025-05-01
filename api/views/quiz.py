import random
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from ..serializers import *
from ..models import *


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


def fetch_quiz_data(quiz_id: int):
    quiz = Quiz.objects.get(id=quiz_id)

    organisms = Organism.objects.all()

    # Apply classification filters if specified
    if quiz.class_name:
        organisms = organisms.filter(classification__class_name__in=quiz.class_name)
    if quiz.order:
        organisms = organisms.filter(classification__order__in=quiz.order)
    if quiz.family:
        organisms = organisms.filter(classification__family__in=quiz.family)
    if quiz.genus:
        organisms = organisms.filter(classification__genus__in=quiz.genus)

    # Ensure image exists
    organisms = organisms.filter(image_url__isnull=False).exclude(image_url='')

    # Handle occurrence status type
    # if occurrence_status_type in occurrence_status_codes:
    #     organisms = organisms.filter(
    #         occurrence_status_verbatim__in=occurrence_status_codes[occurrence_status_type]
    #     )

    organisms = list(organisms)
    random.shuffle(organisms)

    animals = []
    k = 0
    while len(animals) < quiz.max_length and k < len(organisms):
        organism = organisms[k]
        k += 1

        correct_name = organism.name
        animal_class_name = organism.classification.class_name
        animal_order = organism.classification.order
        animal_family = organism.classification.family
        difficulty = quiz.difficulty

        wrong_answers = get_wrong_answers(animal_class_name, animal_order, animal_family, correct_name, difficulty)

        animal = {
            "name": correct_name,
            "class": animal_class_name,
            "order": animal_order,
            "family": animal_family,
            "image": organism.image_url,
            "wrongAnswers": wrong_answers,
        }

        if not any(a["name"] == correct_name for a in animals):
            animals.append(animal)

    return animals


def get_quiz_data(request, quiz_id: int):
    """ API endpoint to get animal data for a given quiz. """
    animals = fetch_quiz_data(quiz_id)
    return JsonResponse(animals, safe=False)


def get_wrong_answers(class_name, order, family, correct_name, difficulty=DifficultyLevel.HARD):
    """ Get wrong answers from the database. """
    base_query = Organism.objects.filter(
        classification__class_name=class_name,
    ).exclude(name=correct_name)

    if difficulty == DifficultyLevel.HARD:
        wrongs = base_query.filter(
            classification__order=order,
            classification__family=family
        )

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
    
    elif difficulty == DifficultyLevel.EASY:
        wrongs = base_query.exclude(classification__order=order)
        if wrongs.count() < 3:
            wrongs = base_query.exclude(classification__family=family)
        if wrongs.count() < 3:
            wrongs = base_query

    wrong_names = list(wrongs.values_list('name', flat=True))
    wrong_names = list(set(wrong_names))  # Remove any duplicates

    while len(wrong_names) < 3:
        # Backup: randomly add names if too few
        extra = Organism.objects.exclude(name=correct_name).order_by('?').values_list('name', flat=True)[:1]
        if extra:
            wrong_names.append(extra[0])

    random.shuffle(wrong_names)
    return wrong_names[:3]


class OrganismViewSet(viewsets.ModelViewSet):
    queryset = Organism.objects.all()
    serializer_class = OrganismSerializer

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer