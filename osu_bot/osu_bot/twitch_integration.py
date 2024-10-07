import json
import os
import requests
import time
import threading
from config import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET

class TwitchIntegration:
    def __init__(self, bot):
        self.bot = bot
        self.client_id = TWITCH_CLIENT_ID
        self.client_secret = TWITCH_CLIENT_SECRET
        self.access_token = None
        self.token_expiration = 0
        self.subscriptions = {}  # {twitch_username: set(osu_usernames)}
        self.known_live_streams = set()
        self.subscriptions_file = "data/twitch_subscriptions/twitch_subscriptions.json"
        self.load_subscriptions()
        self.start_polling()

    def get_access_token(self):
        current_time = time.time()
        if current_time > self.token_expiration:
            url = "https://id.twitch.tv/oauth2/token"
            params = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials"
            }
            response = requests.post(url, params=params)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.token_expiration = current_time + data["expires_in"] - 300
            else:
                raise Exception(f"Failed to get access token: {response.text}")
        return self.access_token

    def load_subscriptions(self):
        if os.path.exists(self.subscriptions_file):
            with open(self.subscriptions_file, 'r') as f:
                loaded_subscriptions = json.load(f)
            self.subscriptions = {k: set(v) for k, v in loaded_subscriptions.items()}
        else:
            self.subscriptions = {}
    
    def save_subscriptions(self):
        subscriptions_to_save = {k: list(v) for k, v in self.subscriptions.items()}
        os.makedirs(os.path.dirname(self.subscriptions_file), exist_ok=True)
        with open(self.subscriptions_file, 'w') as f:
            json.dump(subscriptions_to_save, f)
            
    def subscribe_to_stream(self, osu_username: str, twitch_username: str):
        if twitch_username not in self.subscriptions:
            self.subscriptions[twitch_username] = set()
        self.subscriptions[twitch_username].add(osu_username)
        self.save_subscriptions()
        return True

    def unsubscribe_from_stream(self, osu_username: str, twitch_username: str):
        if twitch_username in self.subscriptions:
            self.subscriptions[twitch_username].discard(osu_username)
            if not self.subscriptions[twitch_username]:
                del self.subscriptions[twitch_username]
            self.save_subscriptions()
        return True

    def check_streams(self):
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.get_access_token()}"
        }
        for twitch_username in self.subscriptions:
            url = f"https://api.twitch.tv/helix/streams?user_login={twitch_username}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()["data"]
                if data and twitch_username not in self.known_live_streams:
                    self.known_live_streams.add(twitch_username)
                    self.handle_stream_online(twitch_username)
                elif not data and twitch_username in self.known_live_streams:
                    self.known_live_streams.remove(twitch_username)
            else:
                print(f"Failed to check stream status for {twitch_username}: {response.text}")

    def handle_stream_online(self, twitch_username: str):
        if twitch_username in self.subscriptions:
            print(f"Stream started: {twitch_username}")
            for osu_username in self.subscriptions[twitch_username]:
                self.bot.send_message(None, osu_username, f"{twitch_username} has started streaming!", True)

    def start_polling(self):
        def poll():
            while True:
                try:
                    self.check_streams()
                except Exception as e:
                    print(f"Error during stream check: {str(e)}")
                time.sleep(60)  # Check every 1 minute

        thread = threading.Thread(target=poll)
        thread.daemon = True
        thread.start()