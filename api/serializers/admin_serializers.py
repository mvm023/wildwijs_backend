from rest_framework import serializers
from ..models import *


class QuizAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

class QuizLayerAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizLayer
        fields = '__all__'

class QuizSubcategoryAdminSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # Add this line to allow passing `id` during updates
    category = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = QuizSubcategory
        fields = '__all__'

class QuizCategoryAdminSerializer(serializers.ModelSerializer):
    subcategories = QuizSubcategoryAdminSerializer(many=True)
    deleted_subcategory_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )


    class Meta:
        model = QuizCategory
        fields = ['id', 'name', 'image_url', 'phylums', 'class_names', 'subcategories', 'deleted_subcategory_ids',]

    def create(self, validated_data):
        subcategories_data = validated_data.pop('subcategories', [])

        category = QuizCategory.objects.create(**validated_data)

        # Create subcategories and related QuizLayers and Quizzes
        for sub_data in subcategories_data:
            QuizSubcategory.objects.create(category=category, **sub_data)

        return category

    def update(self, instance, validated_data):
        # Separate subcategory data
        subcategories_data = validated_data.pop('subcategories', [])
        deleted_subcategory_ids = validated_data.pop('deleted_subcategory_ids', [])
        print(deleted_subcategory_ids)


        # Update the main category fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create subcategories
        for sub_data in subcategories_data:
            # If subcategory already exists, update it
            subcategory_id = sub_data.get('id')
            if subcategory_id:
                try:
                    subcategory = instance.subcategories.get(id=subcategory_id)
                    for attr, value in sub_data.items():
                        setattr(subcategory, attr, value)
                    subcategory.save()
                except QuizSubcategory.DoesNotExist:
                    # If the subcategory doesn't exist, create it
                    QuizSubcategory.objects.create(category=instance, **sub_data)
            else:
                # If there's no ID, create a new subcategory
                sub_data.pop('category', None)  # Remove 'category' from sub_data if it exists
                QuizSubcategory.objects.create(category=instance, **sub_data)

        # Delete subcategories that have been marked for deletion
        for deleted_subcategory_id in deleted_subcategory_ids:
            QuizSubcategory.objects.filter(id=deleted_subcategory_id, category=instance).delete()

        return instance