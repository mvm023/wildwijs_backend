import json
import random
import uuid
from django.http import JsonResponse
from django.conf import settings
from rest_framework import viewsets
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from knox.auth import TokenAuthentication
from ..permissions import IsAdminForUnsafeMethods
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

def start_quiz(request, quiz_id: int):
    quiz = Quiz.objects.get(id=quiz_id)
    questions = fetch_quiz_data(quiz.id)

    # Create a session-based quiz ID
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    quiz_session_id = str(uuid.uuid4())  # client will send this back when answering

    # Store answers in cache (not sent to client)
    question_data = []
    for i, q in enumerate(questions):
        q_id = f"{quiz_session_id}_{i}"
        cache.set(q_id, q["name"], timeout=600)  # Only store the correct name
        question_data.append({
            "image": q["image"],
            "options": q["wrongAnswers"] + [q["name"]],
            "question_id": i  # Needed to validate later
        })

    return JsonResponse({
        "quiz_session_id": quiz_session_id,
        "questions": question_data,
    })

@api_view(['POST'])
@authentication_classes([TokenAuthentication])  # Allows token auth if present
@permission_classes([AllowAny])  # Allows access without authentication
def answer_question(request):
    data = json.loads(request.body)
    quiz_session_id = data["quiz_session_id"]
    question_id = data["question_id"]
    selected = data["selected"]

    print(f"Option {selected} has been selected for question with id {question_id} and quiz session id {quiz_session_id}")

    cache_key = f"{quiz_session_id}_{question_id}"
    correct = cache.get(cache_key)

    if correct is None:
        return JsonResponse({"error": "Invalid question or session"}, status=404)

    return JsonResponse({"correct": selected == correct})


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

@api_view(['POST'])
@authentication_classes([TokenAuthentication])  # Allows token auth if present
@permission_classes([AllowAny])  # Allows access without authentication
def end_quiz(request, quiz_id: int):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.user and request.user.is_authenticated:
        # Logged-in user
        user = request.user
        progress, _ = UserQuizProgress.objects.get_or_create(user=user, quiz=quiz)
        progress.attempts += 1
        if progress.attempts >= quiz.required_attempts:
            progress.completed = True
        progress.save()
        return Response(
            {"message": "Quiz attempt recorded.", "attempts": progress.attempts},
            status=status.HTTP_200_OK
        )

    # Not logged in: do nothing for now
    return Response(
        {"message": "Anonymous users' progress not recorded."},
        status=status.HTTP_200_OK
    )


class OrganismViewSet(viewsets.ModelViewSet):
    queryset = Organism.objects.all()
    serializer_class = OrganismSerializer
    permission_classes = [IsAdminForUnsafeMethods]

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAdminForUnsafeMethods]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user  # Pass the user object to the serializer context
        return context


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = QuizCategory.objects.all()
    serializer_class = QuizCategorySerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user 
        return context


class SubcategoryViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSubCategorySerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        category = get_object_or_404(QuizCategory, id=category_id)
        return category.subcategories.all()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user 
        return context

class QuizBySubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def get_queryset(self):
        subcategory_id = self.kwargs['subcategory_id']
        subcategory = get_object_or_404(QuizSubcategory, id=subcategory_id)
        layers = subcategory.layers.all()
        quizzes = []
        for layer in layers:
            quizzes += layer.quizzes.all()
        return quizzes

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user 
        return context