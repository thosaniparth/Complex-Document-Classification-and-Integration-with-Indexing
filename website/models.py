from django.db import models
import datetime

class PostModel(models.Model):
    name = models.CharField(max_length=130)
    middlename = models.CharField(max_length=130)
    surname = models.CharField(max_length=130)
    dob =  models.DateField(("Date"), default=datetime.date.today)
    image=models.ImageField(blank=True,upload_to="pictures/")
    image1=models.ImageField(blank=True,upload_to="pictures/")




    def __str__(self):
        return str(self.pk)
# # Create your models here.
# class Person(models.Model):
#     name = models.CharField(max_length=130)
#     email = models.EmailField(blank=True)
#     job_title = models.CharField(max_length=30, blank=True)
#     bio = models.TextField(blank=True)
#     image=models.ImageField(blank=True,upload_to="pictures/")