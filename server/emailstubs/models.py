from django.db import models

# Create your models here.

class Message(models.Model):
    from_email = models.CharField(max_length=200)
    to_email = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    contents = models.TextField()
    date = models.DateTimeField()
