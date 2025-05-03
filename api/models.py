from django.db import models
from django.contrib.postgres.fields import ArrayField

class Classification(models.Model):
    kingdom = models.CharField(max_length=150)
    phylum = models.CharField(max_length=150)
    class_name = models.CharField(max_length=150)
    order = models.CharField(max_length=150)
    family = models.CharField(max_length=150)
    genus = models.CharField(max_length=150)
    species = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.genus} {self.species}" 

class Organism(models.Model):
    name = models.CharField(unique=True,max_length=150)
    description = models.TextField(blank=True)
    scientific_name = models.CharField(unique=True,max_length=200)
    classification = models.ForeignKey(Classification, on_delete=models.CASCADE)
    occurrence_status_verbatim = models.CharField(max_length=255, blank=True)  # New field for occurrence status
    alternative_names = models.JSONField(null=True, blank=True)  # New field for alternative names as a list of strings
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now = True)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class QuizCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class QuizLayer(models.Model):
    category = models.ForeignKey(QuizCategory, on_delete=models.CASCADE, related_name='layers')
    level = models.PositiveIntegerField(help_text="The depth level of the layer in this category")
    
    class Meta:
        unique_together = ('category', 'level')
        ordering = ['level']

    def __str__(self):
        return f"{self.category.name} – Layer {self.level}"


class DifficultyLevel(models.TextChoices):
    EASY = 'easy', 'Easy'
    HARD = 'hard', 'Hard'

class Quiz(models.Model):
    name = models.CharField(max_length=255)
    image_url = models.URLField()
    class_name = models.JSONField(default=list, blank=True)
    order = models.JSONField(default=list, blank=True)
    family = models.JSONField(default=list, blank=True)
    genus = models.JSONField(default=list, blank=True)
    max_length = models.PositiveIntegerField(default=15)
    difficulty = models.CharField(
        max_length=10,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.EASY,
    )

    layer = models.ForeignKey(QuizLayer, on_delete=models.CASCADE, related_name='quizzes')

    def __str__(self):
        return self.name