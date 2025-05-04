from django.db import models
from django.conf import settings

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
    image_url = models.URLField()

    def __str__(self):
        return self.name
    
    def completion_progress(self, user):
        total = 0
        completed = 0

        for subcat in self.subcategories.all():
            progress = subcat.completion_progress(user)
            total += progress['total']
            completed += progress['completed']

        percentage = round((completed / total) * 100, 1) if total > 0 else 0.0
        return {
            "completed": completed,
            "total": total,
            "percentage": percentage
        }

    
class QuizSubcategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(QuizCategory, on_delete=models.CASCADE, related_name='subcategories')
    image_url = models.URLField()

    def __str__(self):
        return self.name
    
    def completion_progress(self, user):
        # Gather all quizzes in this subcategory through layers
        all_quizzes = Quiz.objects.filter(layer__sub_category=self)
        total = all_quizzes.count()

        if not user.is_authenticated or total == 0:
            return {"completed": 0, "total": total, "percentage": 0.0}

        completed = UserQuizProgress.objects.filter(
            user=user,
            quiz__in=all_quizzes,
            completed=True
        ).count()

        return {
            "completed": completed,
            "total": total,
            "percentage": round((completed / total) * 100, 1) if total > 0 else 0.0
        }


class QuizLayer(models.Model):
    sub_category = models.ForeignKey(QuizSubcategory, on_delete=models.CASCADE, related_name='layers')
    level = models.PositiveIntegerField(help_text="The depth level of the layer in this subcategory")
    
    class Meta:
        unique_together = ('sub_category', 'level')
        ordering = ['level']
    
    def is_completed_by_user(self, user):
        quizzes_in_layer = self.quizzes.all()
        for quiz in quizzes_in_layer:
            progress = UserQuizProgress.objects.filter(user=user, quiz=quiz).first()
            if not progress or not progress.completed:
                return False
        return True

    def __str__(self):
        return f"{self.sub_category.name} – Layer {self.level}"


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
    required_attempts = models.PositiveIntegerField(default=1, help_text="Number of times this quiz must be completed to mark it as done")
    layer = models.ForeignKey(QuizLayer, on_delete=models.CASCADE, related_name='quizzes')
        
    def completed_attempts(self, user):
        if not user.is_authenticated:
            return 0

        try:
            progress = UserQuizProgress.objects.get(user=user, quiz=self)
            return progress.attempts
        except UserQuizProgress.DoesNotExist:
            return 0  # If the user has no progress
    
    def is_unlocked(self, user):
        # If it's in the first layer (level 0), it's always unlocked
        if self.layer.level == 0:
            return True
        
        if not user.is_authenticated:
            return False
        
        # Get the previous layer (level - 1)
        previous_layer = QuizLayer.objects.filter(
            sub_category=self.layer.sub_category, 
            level=self.layer.level - 1
        ).first()

        if not previous_layer:
            return False  # If there is no previous layer, it's not unlocked
        
        # Check if all quizzes in the previous layer are completed by the user
        quizzes_in_previous_layer = previous_layer.quizzes.all()
        
        for quiz in quizzes_in_previous_layer:
            progress = UserQuizProgress.objects.filter(user=user, quiz=quiz).first()
            if not progress or not progress.completed:
                return False
        
        return True

        

    def __str__(self):
        return self.name
    
class UserQuizProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    attempts = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'quiz')
    
    def __str__(self):
        return f"{self.user.username} – {self.quiz.name} – {self.attempts} attempts"

