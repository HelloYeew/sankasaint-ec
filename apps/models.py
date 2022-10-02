from django.contrib.auth.models import User
from django.db import models


class Area(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Candidate(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(default='default_candidate.png', upload_to='candidates')
    description = models.TextField()
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Election(models.Model):
    name = models.CharField(max_length=100)
    front_image = models.ImageField(default='default_election.png', upload_to='elections')
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return self.name


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ' voted for ' + self.candidate.name + ' in ' + self.election.name
