from django.db import models

# Create your models here.

class LogEntry(models.Model):
    tester = models.TextField()
    tester_comments = models.TextField()
    test_file = models.TextField()
    test_description = models.TextField()

    style = models.TextField()
    url = models.TextField()
    params = models.TextField()
    user = models.IntegerField()
    visit_number = models.IntegerField()
    total_time_to_render = models.IntegerField()
    data_fetch = models.IntegerField()
    data_bulkload = models.IntegerField()
    template_parse = models.IntegerField()
    latency = models.IntegerField()
    bandwidth = models.IntegerField()
        
    date = models.DateTimeField(auto_now_add=True)
