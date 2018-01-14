from django.db import models

# Create your models here.
class Summoner(models.Model):
    summoner_id = models.IntegerField(unique=True, null=False)
    name = models.CharField(unique=True, null=False, max_length=32)

class Match(models.Model):
    result = models.BooleanField(null=False)
    game_id = models.IntegerField(unique=True, null=False)
    champ_id = models.IntegerField(unique=True, null=False)
    summoner_id = models.IntegerField(unique=True, null=False)

class Champion(models.Model):
    champion_id = models.IntegerField(unique=True, null=False)
    name = models.CharField(unique=True, null=False, max_length=12)
    palette = models.CharField(null=False, max_length=64)

