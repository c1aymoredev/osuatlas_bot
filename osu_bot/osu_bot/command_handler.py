from services.osu_api_client import OsuAPIClient
from services.pp_calculator import PPCalculator
from utils.utils import parse_mods
from services.beatmap_recommender import BeatmapRecommender

class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        self.api_client = OsuAPIClient()
        self.pp_calculator = PPCalculator()
        self.recommender = BeatmapRecommender()

    def handle_pp_command(self, message: str) -> str:
        parts = message.split()
        if len(parts) < 2:
            return "Please provide map ID."
        
        map_id = parts[1]
        mods_str = ' '.join(parts[2:]) if len(parts) > 2 else 'NM'
        
        try:
            mods = parse_mods(mods_str.split())
            beatmap_path = self.api_client.download_map(map_id)
            map_info = self.api_client.get_map_info(map_id)
            print(f"Debug - map_info: {map_info}")  # Добавьте эту строку для отладки
            pp_values, stars, ar, od, cs, hp = self.pp_calculator.calculate_pp(beatmap_path, mods)
            return self.pp_calculator.format_pp_result(map_info, pp_values, stars, ar, od, cs, hp, mods)
        except ValueError as e:
            return f"Error: {str(e)}"
        except ConnectionError as e:
            return f"Error downloading map: {str(e)}"
        except Exception as e:
            return f"An unknown error occurred: {str(e)}"

    def handle_with_command(self, message: str, sender: str) -> str:
        if sender not in self.bot.last_map:
            return "First use the /np or !pp command to select a map."
        
        parts = message.split()
        if len(parts) < 2:
            return "Please specify mods. Example: !with HDDT"
        
        new_mods = ' '.join(parts[1:])
        map_id = self.bot.last_map[sender]['id']
        
        return self.handle_pp_command(f"!pp {map_id} {new_mods}")

    def handle_recommendation_command(self, message: str, sender: str) -> str:
        params = message.split()[1:]
        return self.recommender.get_recommendation(sender, params)