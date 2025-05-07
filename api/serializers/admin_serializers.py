from rest_framework import serializers
from ..models import *

class QuizCategoryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizCategory
        fields = '__all__'
