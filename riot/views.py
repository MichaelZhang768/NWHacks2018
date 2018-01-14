from django.shortcuts import render
from django.http import HttpResponse
import json
from riot.riot import RiotManager
from riot import config
from riot.models import Champion
from riot.data import DataProcessingManager

def index(request):
    return HttpResponse("Hello, world. You're at the Riot index.")

def get_palette(request):
    results = {}
    dpm = DataProcessingManager()
    champ_name = request.GET.get('champion_name')

    try:
        if not champ_name:
            raise ValueError("Query param 'champion_name' required")

        champ_id = None
        for k, v in config.CHAMP_ID_TO_NAME.items():
            if v.lower() == champ_name.lower():
                champ_id = k
                break

        if not champ_id:
            raise ValueError("Champion name: %s is not a valid name" % champ_name)

        palette = dpm.get_palette_from_champion(champ_id=champ_id)

        results['results'] = palette.split()
        resp = HttpResponse(json.dumps(results))
    except ValueError as e:
        results['error'] = str(e)
        resp = HttpResponse(json.dumps(results), status=400)

    resp['Access-Control-Allow-Origin'] = "*"
    resp['Content-Type'] = "application/json"
    return resp

def get_and_store_summoner_data(request):
    rm = RiotManager()
    name = request.GET.get('name')

    try:
        return rm.get_and_store_summoner_data(name)
    except Exception as e:
        results = {'error': str(e)}
        return HttpResponse(json.dumps(results), content_type='application/json')
