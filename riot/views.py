from django.shortcuts import render
from django.http import HttpResponse

from riot import config
from riot.models import Champion
from riot.data import DataProcessingManager

def index(request):
    return HttpResponse("Hello, world. You're at the Riot index.")

def get_palette(request):
    dpm = DataProcessingManager()
    champ_name = request.GET.get('champion_name')

    for k, v in config.CHAMP_ID_TO_NAME.items():
        champ_id = k
        if v.lower() == champ_name.lower():
            break

    return HttpResponse(dpm.get_palette_from_champion(champ_id=champ_id))
