import re
import logging
from typing import List, Optional, Tuple
from services.osu_api_client import OsuAPIClient

class NPHandler:
    NP_PATTERN = re.compile(
        r"(?:\* (?P<username>\w+)\s*)?"
        r"(?:/np\s+)?"
        r"(?:is\s+)?"
        r"(?:listening to|playing|watching|editing)?\s*"
        r"(?:\[)?"
        r"(?P<url>https?://osu\.ppy\.sh/beatmapsets/(?P<beatmapset_id>\d+)(?:#osu/|#/)?(?P<beatmap_id>\d+))"
        r"(?:\s+(?P<artist>.+?) - (?P<title>.+?)(?:\s+\[(?P<version>.+?)\])?)?"
        r"(?:\])?"
        r"(?:\s*(?P<mods>(?:[-+](?:Easy|NoFail|HalfTime|HardRock|SuddenDeath|DoubleTime|Nightcore|Hidden|Flashlight|SpunOut|Autopilot|Perfect)(?:\s+)?)+))?\s*$"
    )

    def __init__(self, bot):
        self.bot = bot
        self.api_client = OsuAPIClient()

    def handle(self, message: str, sender: str) -> Optional[str]:
        try:
            beatmap_with_mods = self.parse_np(message)
            if not beatmap_with_mods:
                return None
            
            beatmap_id, mods, artist, title = beatmap_with_mods
            mods_string = ' '.join(mods)
            response = self.bot.command_handler.handle_pp_command(f"!pp {beatmap_id} {mods_string}")
            self.bot.last_map[sender] = {'id': beatmap_id, 'mods': mods}
            return response
        except Exception as e:
            logging.error(f"Ошибка при обработке NP сообщения: {str(e)}", exc_info=True)
            return f"Произошла ошибка при обработке NP сообщения: {str(e)}"

    def parse_np(self, message: str) -> Optional[Tuple[int, List[str], str, str]]:
        match = self.NP_PATTERN.search(message)
        if not match:
            logging.error(f"NP сообщение не совпадает с паттерном: {message}")
            return None
        
        self.log_match_groups(match)
        
        beatmap_id = match.group("beatmap_id")
        if not beatmap_id:
            beatmap_id = match.group("beatmapset_id")
        beatmap_id = int(beatmap_id)
        artist = match.group("artist")
        title = match.group("title")
        version = match.group("version")
        
        if artist is None or title is None:
            try:
                map_info = self.api_client.get_map_info(str(beatmap_id))
                if map_info:
                    artist = map_info['artist']
                    title = map_info['title']
                    version = map_info['version']
                else:
                    artist = "Unknown Artist"
                    title = "Unknown Title"
                    version = "Unknown Difficulty"
            except Exception as e:
                logging.error(f"Ошибка при получении информации о карте: {str(e)}")
                artist = "Unknown Artist"
                title = "Unknown Title"
                version = "Unknown Difficulty"
        
        artist = artist.strip() if artist else "Unknown Artist"
        title = title.strip() if title else "Unknown Title"
        version = version.strip() if version else "Unknown Difficulty"
        
        mods_str = match.group("mods") or ""
        mods_list = mods_str.split()
        
        full_title = f"{title} [{version}]"
        logging.info(f"Извлеченные данные: ID={beatmap_id}, Моды={mods_list}, Исполнитель={artist}, Название={full_title}")
        return (beatmap_id, mods_list, artist, full_title)

    def log_match_groups(self, match):
        if match:
            for group_name in match.groupdict():
                logging.info(f"Group {group_name}: {match.group(group_name)}")
        else:
            logging.info("No match found")