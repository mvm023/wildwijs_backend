from django.db import models

# Create your models here.

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
    description = models.CharField(max_length=1000)
    scientific_name = models.CharField(unique=True,max_length=200)
    classification = models.ForeignKey(Classification, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.name