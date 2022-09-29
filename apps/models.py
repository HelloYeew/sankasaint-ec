from django.db import models


class Area(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Candidate(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='candidates')
    description = models.TextField()
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)

