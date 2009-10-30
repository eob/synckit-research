from django.db import models

# Create your models here.

class Page(models.Model):
    outlinks = models.ManyToManyField('self', related_name='inlinks', symmetrical=False)
    title = models.TextField()
    contents = models.TextField()
    access_probability = models.FloatField()
    date = models.DateTimeField(db_index=True)
