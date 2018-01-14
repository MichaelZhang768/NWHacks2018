import requests
import urllib.parse

class RiotApi(object):

    API_ROOT = 'https://na1.api.riotgames.com/lol/'

    def get_matches(self, player_id, params, headers):
        url = API_ROOT + "match/v3/matches/" + player_id
        return requests.get(url, params=params, headers=headers)

