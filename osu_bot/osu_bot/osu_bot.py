from .irc_client import IRCClient
from .command_handler import CommandHandler
from .np_handler import NPHandler
from services.osu_api_client import OsuAPIClient
from services.pp_calculator import PPCalculator
from services.beatmap_recommender import BeatmapRecommender
from utils.utils import UserException

class OsuBot:
    def __init__(self):
        self.irc_client = IRCClient(self)
        self.command_handler = CommandHandler(self)
        self.np_handler = NPHandler(self)
        self.api_client = OsuAPIClient()
        self.pp_calculator = PPCalculator()
        self.recommender = BeatmapRecommender()
        self.last_map = {}

    def start(self):
        self.irc_client.start()

    def handle_message(self, message: str, connection, sender: str, is_private: bool = False):
        try:
            if message.startswith("!pp"):
                response = self.command_handler.handle_pp_command(message)
            elif "is listening to" in message or "is playing" in message or "is watching" in message or "is editing" in message or message.startswith("/np"):
                response = self.np_handler.handle(message, sender)
            elif message.startswith("!with"):
                response = self.command_handler.handle_with_command(message, sender)
            elif message.startswith("!r"):
                response = self.command_handler.handle_recommendation_command(message, sender)
            else:
                response = "Неизвестная команда"
            
            if response:
                self.send_message(connection, sender, response, is_private)
        except UserException as e:
            self.send_message(connection, sender, str(e), is_private)
        except Exception as e:
            self.send_message(connection, sender, f"Произошла ошибка: {str(e)}", is_private)

    def send_message(self, connection, target: str, message: str, is_private: bool):
        self.irc_client.send_message(connection, target, message, is_private)