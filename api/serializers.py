from rest_framework import serializers
from .models import *

class ClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classification
        fields = "__all__"

class OrganismSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organism
        fields = ('id','name','description','scientific_name','classification')

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = "__all__"
