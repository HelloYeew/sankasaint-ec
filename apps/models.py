from django.contrib.auth.models import User
from django.db import models


class LegacyArea(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class LegacyCandidate(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(default='default_candidate.png', upload_to='candidates')
    description = models.TextField()
    area = models.ForeignKey(LegacyArea, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default_candidate.png', upload_to='candidates')
    description = models.TextField()
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username + ' - ' + self.area.name


class LegacyElection(models.Model):
    name = models.CharField(max_length=100)
    front_image = models.ImageField(default='default_election.png', upload_to='elections')
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

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


class LegacyVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(LegacyCandidate, on_delete=models.CASCADE)
    election = models.ForeignKey(LegacyElection, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ' voted for ' + self.candidate.name + ' in ' + self.election.name


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ' voted in ' + self.election.name + ' at ' + self.time.strftime('%Y-%m-%d %H:%M:%S')


class VoteResultParty(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    party = models.ForeignKey(Area, on_delete=models.CASCADE)
    vote = models.IntegerField(default=0)

    def __str__(self):
        return self.election.name + ' - ' + self.party.name + ' - ' + str(self.vote)


class VoteResultCandidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    vote = models.IntegerField(default=0)

    def __str__(self):
        return self.election.name + ' - ' + self.candidate.user.username + ' - ' + str(self.vote)


class LegacyParty(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(default='default_party.png', upload_to='parties')
    candidates = models.ManyToManyField(LegacyCandidate)

    def __str__(self):
        return self.name


class Party(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(default='default_party.png', upload_to='parties')
    candidates = models.ManyToManyField(Candidate)

    def __str__(self):
        return self.name
