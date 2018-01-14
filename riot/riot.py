from riot import secrets
from copy import deepcopy
from riot.models import Summoner, Match
import requests
import time
import datetime

from riot import config

class RiotManager(object):
    def __init__(self):
        self.keys = secrets.RIOT_KEYS
        self.current_secret_idx = 0
        self.current_secret = self.keys[self.current_secret_idx]

    def get_params_with_auth(self, param={}):
        dup_param = deepcopy(param)
        dup_param['api_key'] = self.get_current_secret()
        return dup_param

    def get_current_secret(self, skip_incr=False):
        return_val = self.current_secret
        if not skip_incr:
            self.current_secret_idx = (self.current_secret_idx + 1) % len(self.keys)
            self.current_secret = self.keys[self.current_secret_idx]
            print(self.current_secret)
        return return_val

    def get_summoner_data(self, name):
        url = '%ssummoner/v3/summoners/by-name/%s' % (config.RIOT_API_ROOT, name)
        return requests.get(url, params=self.get_params_with_auth()).json()

    def get_matches(self, account_id):
        url = '%smatch/v3/matchlists/by-account/%d' % (config.RIOT_API_ROOT, account_id)
        return requests.get(url, params=self.get_params_with_auth()).json()

    def get_match(self, match_id):
        url = '%smatch/v3/matches/%d' % (config.RIOT_API_ROOT, match_id)
        return requests.get(url, params=self.get_params_with_auth()).json()

    def get_won_match(self, account_id, match):
        participant_id = ""
        participants = match['participantIdentities']
        for participant in participants:
            if(participant['player']['accountId'] == account_id):
                participant_id = participant['participantId']
                break;

        participants_data = match['participants']
        team_id = 0;
        for participant_data in participants_data:
            if(participant_data['participantId'] == participant_id):
                team_id = participant_data['teamId']
                break;

        if(team_id == 100):
            return match['teams'][0]['win'] == 'Win'
        else:
            return match['teams'][1]['win'] == 'Win'


    def store_summoner_data(self, name):
        rm = RiotManager()
        summoner_data = rm.get_summoner_data(name)
        account_id = summoner_data['accountId']

        Summoner.objects.get_or_create(account_id=account_id, name=name)

        matchDicts = []
        matches = rm.get_matches(account_id)

        for match in matches['matches']:
            matchDicts.append({'gameId' : match['gameId'],
                               'matchData' : rm.get_match(match['gameId']),
                               'champion' : match['champion'],
                               'timestamp' : match['timestamp']})

        for matchDict in matchDicts:
            try:
                result=rm.get_won_match(account_id, matchDict['matchData'])
                Match.objects.create(timestamp=datetime.datetime.fromtimestamp(matchDict['timestamp']/1000.0),
                                     result=result, game_id=matchDict['gameId'],
                                     champ_id=matchDict['champion'], account_id=account_id)
            except Exception as e:
                print(e)
            

        
