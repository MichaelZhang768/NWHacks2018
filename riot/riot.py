from riot import secrets
from copy import deepcopy
from riot.models import Summoner, Match
from django.http import HttpResponse
import requests
import time
import datetime
import json

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
        return return_val

    def get_summoner_data(self, name):
        url = '%ssummoner/v3/summoners/by-name/%s' % (config.RIOT_API_ROOT, name)
        return requests.get(url, params=self.get_params_with_auth()).json()

    def get_matches(self, account_id, begin_index=0, end_index=80):
        url = '%smatch/v3/matchlists/by-account/%d?beginIndex=%d&endIndex=%d' % (config.RIOT_API_ROOT,
                                                                                 account_id, begin_index, end_index)
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

    def add_match_info_to_db(self, matchDicts):
        for matchDict in matchDicts:
            try:
                Match.objects.create(timestamp=matchDict['timestamp'], result=matchDict['result'],
                                     game_id=matchDict['gameId'], champ_id=matchDict['champId'],
                                     account_id=matchDict['accountId'])
            except Exception as e:
                print(e)

    def get_and_store_summoner_data(self, name):
        rm = RiotManager()
        summoner_data = rm.get_summoner_data(name)
        account_id = summoner_data['accountId']

        Summoner.objects.get_or_create(account_id=account_id, name=name)
        matches = rm.get_matches(account_id)
        match_list = matches['matches']
        total_games = matches['totalGames']
        
        matchDicts = []
        cached_game_ids = []

        db_matches = set(Match.objects.filter(account_id=account_id))
        continue_requesting = len(db_matches) > total_games

        calls_to_get_matches = (total_games/80)-2
        last_call_to_get_matches = total_games%80
        begin_index = 80

        while(calls_to_get_matches > 0):
            more_matches = rm.get_matches(account_id, begin_index, begin_index+80)
            match_list.extend(more_matches['matches'])
            begin_index+=80
            calls_to_get_matches-=1

        if(last_call_to_get_matches > 0):
            more_matches = rm.get_matches(account_id, total_games-last_call_to_get_matches, total_games)
            match_list.extend(more_matches['matches'])
        
        for db_match in db_matches:
            cached_game_ids.append(db_match.game_id)
            matchDicts.append({'gameId' : db_match.game_id,
                               'accountId' : db_match.account_id,
                               'result' : db_match.result,
                               'timestamp' : db_match.timestamp.strftime("%Y-%m-%d"),
                               'champId' : db_match.champ_id})

        cached_game_ids = set(cached_game_ids)
        match_list_ids = set(map(lambda x: x['gameId'], match_list))
        difference = match_list_ids - cached_game_ids

        matches_to_fetch = [match for match in match_list if match['gameId'] in difference]
            
        number_of_matches = len(matches_to_fetch)    

        matches_to_process = min(number_of_matches, 80)

        new_match_dicts = []

        get_match_counter = 0
        for match in matches_to_fetch:
            try:
                match_data = rm.get_match(match['gameId'])
                get_match_counter+=1
                new_match_dicts.append({'gameId' : match['gameId'],
                                'accountId' : account_id,   
                                'result' : rm.get_won_match(account_id, match_data),
                                'champId' : match['champion'],
                                'timestamp' : datetime.datetime.fromtimestamp(match['timestamp']/1000.0).strftime("%Y-%m-%d")})
                time.sleep(1.5)
            except Exception as e:
                print(get_match_counter)
                print(e)
                time.sleep(60)
            
        self.add_match_info_to_db(new_match_dicts)
        matchDicts.extend(new_match_dicts)

        champ_games_played = {}
        for matchDict in matchDicts:
            if config.CHAMP_ID_TO_NAME[matchDict['champId']] not in champ_games_played:
                champ_games_played[config.CHAMP_ID_TO_NAME[matchDict['champId']]] = 1
            else:
                champ_games_played[config.CHAMP_ID_TO_NAME[matchDict['champId']]] += 1

        champ_games_won = {}
        for matchDict in matchDicts:
            if config.CHAMP_ID_TO_NAME[matchDict['champId']] not in champ_games_won:
                champ_games_won[config.CHAMP_ID_TO_NAME[matchDict['champId']]] = 1
            else:
                champ_games_won[config.CHAMP_ID_TO_NAME[matchDict['champId']]] += 1

        month_year_champs_played = {}
        db_matches = Match.objects.filter(account_id=account_id).order_by('-timestamp')
        match_dicts = []
        for db_match in db_matches:
            match_dicts.append({'gameId' : db_match.game_id,
                               'accountId' : db_match.account_id,
                               'result' : db_match.result,
                               'timestamp' : db_match.timestamp.strftime("%Y-%m-%d"),
                               'champId' : db_match.champ_id})

        year_month = ""
        for matchDict in match_dicts:
            if year_month != matchDict['timestamp'][0:7]:
                year_month = matchDict['timestamp'][0:7]
                if year_month not in month_year_champs_played:
                    month_year_champs_played[year_month] = {}
                    month_year_champs_played[year_month][config.CHAMP_ID_TO_NAME[matchDict['champId']]] = 1
                else:
                    if config.CHAMP_ID_TO_NAME[matchDict['champId']] not in month_year_champs_played[year_month]:
                        month_year_champs_played[year_month][config.CHAMP_ID_TO_NAME[matchDict['champId']]] = 1
                    else:
                        month_year_champs_played[year_month][config.CHAMP_ID_TO_NAME[matchDict['champId']]] += 1
            else:
                if config.CHAMP_ID_TO_NAME[matchDict['champId']] not in month_year_champs_played[year_month]:
                    month_year_champs_played[year_month][config.CHAMP_ID_TO_NAME[matchDict['champId']]] = 1
                else:
                    month_year_champs_played[year_month][config.CHAMP_ID_TO_NAME[matchDict['champId']]] += 1

        response = {'result' : matchDicts,
                    'champ_games_played' : champ_games_played,
                    'champ_games_won' : champ_games_won,
                    'month_year_champs_played' : month_year_champs_played}

        return HttpResponse(json.dumps(response), content_type='application/json')
        
            
            

        
