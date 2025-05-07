from rest_framework import serializers
from ..models import *

class QuizCategoryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizCategory
        fields = '__all__'

class QuizSubcategoryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSubcategory
        fields = '__all__'

class QuizLayerAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizLayer
        fields = '__all__'

class QuizAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'