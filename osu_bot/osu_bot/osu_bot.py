from .irc_client import IRCClient
from .command_handler import CommandHandler
from .np_handler import NPHandler
from services.osu_api_client import OsuAPIClient
from services.pp_calculator import PPCalculator
from services.beatmap_recommender import BeatmapRecommender
from utils.utils import UserException
from .twitch_integration import TwitchIntegration


class OsuBot:
    def __init__(self):
        self.irc_client = IRCClient(self)
        self.command_handler = CommandHandler(self)
        self.np_handler = NPHandler(self)
        self.api_client = OsuAPIClient()
        self.pp_calculator = PPCalculator()
        self.recommender = BeatmapRecommender()
        self.twitch_integration = TwitchIntegration(self)
        self.last_map = {}

    def start(self):
        self.irc_client.start()

    def handle_message(self, message: str, connection, sender: str, is_private: bool = False):
        try:
            if message.startswith("!help"):
                response = self.command_handler.handle_help_command()
            elif message.startswith("!pp"):
                response = self.command_handler.handle_pp_command(message, sender)
            elif "is listening to" in message or "is playing" in message or "is watching" in message or "is editing" in message or message.startswith("/np"):
                response = self.np_handler.handle(message, sender)
            elif message.startswith("!with"):
                response = self.command_handler.handle_with_command(message, sender)
            elif message.startswith("!r"):
                response = self.command_handler.handle_recommendation_command(message, sender)
            elif message.startswith("!notifyme"):
                response = self.command_handler.handle_notifyme_command(message, sender)
            elif message.startswith("!stats"):
                response = self.command_handler.handle_stats_command(message)
            elif message.startswith("!compare"):
                response = self.command_handler.handle_compare_command(message)
            elif message.startswith("!fc"):
                response = self.command_handler.handle_fc_command(message, sender)
            else:
                response = "Unknown command. Type !help for a list of available commands."
            
            if response:
                self.send_message(connection, sender, response, is_private)
        except UserException as e:
            self.send_message(connection, sender, str(e), is_private)
        except Exception as e:
            self.send_message(connection, sender, f"An error occurred: {str(e)}", is_private)

    def send_message(self, connection, target: str, message: str, is_private: bool):
        # Заменяем символы новой строки на пробелы
        message = message.replace('\n', ' ').replace('\r', '')
        
        # Разбиваем длинные сообщения на части
        max_length = 400  # Максимальная длина сообщения IRC
        messages = [message[i:i+max_length] for i in range(0, len(message), max_length)]
        
        if connection:
            for msg in messages:
                if is_private:
                    connection.privmsg(target, msg)
                else:
                    connection.privmsg(self.channel, msg)
        else:
            print(f"Message sent to {target}: {message}")