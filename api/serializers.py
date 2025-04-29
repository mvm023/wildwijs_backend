from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

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

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user