from secrets import secrets
from copy import deepcopy
import requests

from riot import config

class RiotManager(object):
    def __init__(self):
        self.keys = secrets.RIOT_KEYS
        self.current_secret_idx = 0
        self.current_secret = self.keys[self.current_secret_idx]

    def get_params_with_auth(self, param):
        dup_param = deepcopy(param)
        dup_param['api_key'] = self.get_current_secret()
        return dup_param

    def get_current_secret(self, skip_incr=False):
        return_val = self.current_secret
        if not skip_incr:
            self.current_secret_idx = (self.current_secret_idx + 1) % len(self.keys)
            self.current_secret = self.keys[self.current_secret_idx]
        return return_val

    def get_matches(self, account_id, params):
        url = '%smatch/v3/matchlists/by-account/%d' % (config.RIOT_API_ROOT, account_id)
        return requests.get(url, params=self.get_params_with_auth(params))
