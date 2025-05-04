from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Classification)
admin.site.register(Organism)
admin.site.register(Quiz)
admin.site.register(QuizLayer)
admin.site.register(QuizCategory)
admin.site.register(QuizSubcategory)
admin.site.register(UserQuizProgress)