from django.db import models

# Create your models here.
class Summoner(models.Model):
    id = models.IntegerField(unique=True, null=False)
    name = models.CharField(unique=True, null=False, max_length=32)

class Match(models.Model):
    result = models.BooleanField(null=False)
    gameId = models.IntegerField(unique=True, null=False)
    champId = models.IntegerField(unique=True, null=False)
    summonerId = models.IntegerField(unique=True, null=False)

