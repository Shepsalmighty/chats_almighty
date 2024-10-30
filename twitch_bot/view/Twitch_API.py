from functools import lru_cache

import requests
from twitchAPI.twitch import Twitch


class TwitchAPI_call:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.twitch.tv/helix"
        self.access_token = None

    def get_access_token(self):
        """
        Get OAuth access token from Twitch.
        """
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        response = requests.post(url, params=params)

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            return self.access_token
        else:
            raise Exception(f"Error getting access token: {response.json()}")

    @lru_cache
    def get_users(self, username):
        """
        Fetch user data by usernames.

        :param username: List containing Twitch username.
        :return: List of user data.
        """
        if not self.access_token:
            self.get_access_token()

        url = f"{self.base_url}/users"
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }
        params = {
            "login": username
        }

        response = requests.get(url, headers=headers, params=params)

        return response.status_code == 200
        # return response.json().get('data', [])
