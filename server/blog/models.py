from django.db import models

# Create your models here.

class Tag(models.Model):
    text = models.CharField(max_length=200)

class Author(models.Model):
    name = models.CharField(max_length=200)

class Entry(models.Model):
    author = models.ForeignKey(Author)
    title = models.CharField(max_length=200)
    contents = models.TextField()
    date = models.DateTimeField(db_index=True)
    tags = models.ManyToManyField(Tag)
