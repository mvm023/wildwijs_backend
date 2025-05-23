# Generated by Django 5.2 on 2025-05-07 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_rename_class_name_quiz_class_names_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizcategory',
            name='class_names',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='quizcategory',
            name='families',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='quizcategory',
            name='genera',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='quizcategory',
            name='orders',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='quizcategory',
            name='phylums',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='quizsubcategory',
            name='class_names',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='quizsubcategory',
            name='families',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='quizsubcategory',
            name='genera',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='quizsubcategory',
            name='orders',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='quizsubcategory',
            name='phylums',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
