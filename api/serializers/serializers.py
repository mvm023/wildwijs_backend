from rest_framework import serializers
from ..models import *
from django.contrib.auth.models import User


class OrganismSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organism
        fields = ('id','name','description','scientific_name','classification', 'image_url')

class QuizLayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizLayer
        fields = ['id', 'level', 'sub_category']


class QuizSerializer(serializers.ModelSerializer):
    layer = QuizLayerSerializer()

    class Meta:
        model = Quiz
        fields = "__all__"  

    def get_is_unlocked(self, obj):
        user = self.context.get('user')  # Access user from context
        return obj.is_unlocked(user)  # Call the method to check if the quiz is unlocked

    def get_completed_attempts(self, obj):
        user = self.context.get('user')  # Access user from context
        return obj.completed_attempts(user)  # Call the method to check completed attempts

    # Override the default field behavior to add "is_unlocked"
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['is_unlocked'] = self.get_is_unlocked(instance)  # Add the unlocked status
        representation['completed_attempts'] = self.get_completed_attempts(instance)  # Add the unlocked status
        return representation

class QuizSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSubcategory
        fields = ("name", "image_url", "id")
        extra_fields = ["completion_progress"]
    
    def get_completion_progress(self, obj):
        user = self.context.get('user')
        return obj.completion_progress(user)
    
    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation["completion_progress"] = self.get_completion_progress(instance)
        return representation
    
class QuizCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizCategory
        fields = ("name", "image_url", "id")
        extra_fields = ["completion_progress"]
    
    def get_completion_progress(self, obj):
        user = self.context.get('user')
        return obj.completion_progress(user)
    
    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation["completion_progress"] = self.get_completion_progress(instance)
        return representation


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password')
        extra_kwargs = { 'password': {'write_only':True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.is_active = False  # Require email confirmation
        user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop('password', None)
        return ret
