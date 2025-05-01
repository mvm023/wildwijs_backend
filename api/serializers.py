from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

class ClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classification
        fields = "__all__"

class OrganismSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organism
        fields = ('id','name','description','scientific_name','classification')

class QuizLayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizLayer
        fields = ['id', 'level', 'category']


class QuizSerializer(serializers.ModelSerializer):
    layer = QuizLayerSerializer()

    class Meta:
        model = Quiz
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        user.is_active = False  # Require email confirmation
        user.save()
        return user

class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']