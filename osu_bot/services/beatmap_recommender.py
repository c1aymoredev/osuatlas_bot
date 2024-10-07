import random
from typing import List, Dict, Any, Optional
from config import MODS
from services.osu_api_client import OsuAPIClient
from utils.utils import apply_mods_to_difficulty, ar_to_ms, mods_to_int, mods_to_string, ms_to_ar, ms_to_od, od_to_ms

class BeatmapRecommender:
    def __init__(self):
        self.api_client = OsuAPIClient()
        self.recommended_maps = {}

    def get_recommendation(self, username: str, params: List[str]) -> str:
        top_scores = self.api_client.get_user_top_scores(username)
        average_pp = self.api_client.calculate_average_pp(top_scores)

        tags = [param.lower() for param in params if param.lower() in ["aim", "speed", "nm", "consistency", "tech"]]
        mods = [param.upper() for param in params if param.upper() in MODS.keys()]
        
        mods_string = ''.join(mods) if mods else 'NoMod'

        recommended_map = self._get_recommendation(average_pp, mods_string, tags, self.recommended_maps.get(username, set()))
        if not recommended_map:
            return "Нет подходящих карт для вас с заданными параметрами ;("

        self.recommended_maps.setdefault(username, set()).add(recommended_map['id'])

        return self._format_recommended_beatmap(recommended_map, mods_string)

    def _get_recommendation(self, user_pp: float, mods: str, tags: List[str], recommended_maps: set) -> Optional[Dict[str, Any]]:
        suitable_maps = []
        
        for beatmap in self.api_client.load_map_recommendations():
            if beatmap['id'] in recommended_maps:
                continue

            if mods not in beatmap['PP']:
                continue
            
            if tags and not set(tags).issubset(set(beatmap['tags'])):
                continue
            
            pp_values = beatmap['PP'].get(mods, beatmap['PP']['NoMod'])
            
            if not (user_pp - 100 <= pp_values['99'] <= user_pp + 100):
                continue
            
            suitable_maps.append(beatmap)

        return random.choice(suitable_maps) if suitable_maps else None

    def _format_recommended_beatmap(self, map_info: Dict[str, Any], mods: str) -> str:
        beatmap_url = f"https://osu.ppy.sh/beatmaps/{map_info['id']}"
    
        mods_int = mods_to_int(mods) if isinstance(mods, str) else mods
        
        ar = map_info['AR']
        od = map_info['OD']
        cs = map_info['CS']
        hp = map_info['HP']
        bpm = map_info['BPM']
        
        if mods_int & (MODS['DT']['mask'] | MODS['NC']['mask']):
            ar = ms_to_ar(ar_to_ms(ar) * 2/3)
            od = ms_to_od(od_to_ms(od) * 2/3)
            bpm *= 1.5
        elif mods_int & MODS['HT']['mask']:
            ar = ms_to_ar(ar_to_ms(ar) * 4/3)
            od = ms_to_od(od_to_ms(od) * 4/3)
            bpm *= 0.75
        
        if mods_int & MODS['HR']['mask']:
            ar = min(ar * 1.4, 10)
            od = min(od * 1.4, 10)
            cs = min(cs * 1.3, 10)
            hp = min(hp * 1.4, 10)
        elif mods_int & MODS['EZ']['mask']:
            ar *= 0.5
            od *= 0.5
            cs *= 0.5
            hp *= 0.5
        
        pp_values = map_info['PP'].get(mods, map_info['PP']['NoMod'])
        
        stars = apply_mods_to_difficulty(map_info['difficulty'], mods_int)
        
        return (
            f"[{beatmap_url} {map_info['artist']} - {map_info['title']} [{map_info['version']}]] "
            f"+{mods_to_string(mods_int)} "
            f"| {stars:.2f}★ "
            f"| ♫:{bpm:.0f} "
            f"| AR:{ar:.2f} OD:{od:.2f} "
            f"CS:{cs:.1f} HP:{hp:.1f} "
            f"| PP: 95%: {pp_values['95']:.2f}pp, 98%: {pp_values['98']:.2f}pp, 99%: {pp_values['99']:.2f}pp, 100%: {pp_values['100']:.2f}pp"
        )