from django.db import models

# Create your models here.
class Summoner(models.Model):
    account_id = models.IntegerField(unique=True, null=False)
    name = models.CharField(unique=True, null=False, max_length=32)

class Match(models.Model):
    timestamp = models.DateField(null=True)
    result = models.BooleanField(null=False)
    game_id = models.BigIntegerField(null=False)
    champ_id = models.IntegerField(null=False)
    account_id = models.IntegerField(null=False)

    class Meta:
        unique_together = ('game_id', 'account_id')

    
class Champion(models.Model):
    champion_id = models.IntegerField(unique=True, null=False)
    name = models.CharField(unique=True, null=False, max_length=12)
    palette = models.CharField(null=False, max_length=64)
