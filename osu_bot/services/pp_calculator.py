from typing import Dict, Tuple
from rosu_pp_py import Beatmap, Performance
from utils.utils import calculate_bpm, mods_to_string

class PPCalculator:
    def calculate_pp(self, beatmap_path: str, mods: int) -> Tuple[Dict[str, int], float, float, float, float, float]:
        beatmap = Beatmap(path=beatmap_path)
        pp_values = {}
        
        for acc in [95, 98, 99, 100]:
            perf = Performance(accuracy=acc, mods=mods)
            attrs = perf.calculate(beatmap)
            pp_values[str(acc)] = round(attrs.pp)
        
        difficulty_attrs = Performance(mods=mods).calculate(beatmap)
        stars = difficulty_attrs.difficulty.stars
        ar = difficulty_attrs.difficulty.ar
        od = difficulty_attrs.difficulty.od
        cs = beatmap.cs
        hp = beatmap.hp

        return pp_values, stars, ar, od, cs, hp

    def format_pp_result(self, map_info: Dict, pp_values: Dict[str, int], stars: float, ar: float, od: float, cs: float, hp: float, mods: int) -> str:
        mods_string = mods_to_string(mods)
        beatmap_url = f"https://osu.ppy.sh/beatmapsets/{map_info['beatmapset_id']}#osu/{map_info['beatmap_id']}"
        
        return (
            f"[{beatmap_url} {map_info['artist']} - {map_info['title']} [{map_info['version']}]] "
            f"{mods_string}| "
            f"{stars:.2f}★ "
            f"| ♫:{calculate_bpm(float(map_info['bpm']), mods)} "
            f"| AR:{ar:.1f} OD:{od:.1f} CS:{cs:.1f} HP:{hp:.1f} "
            f"| PP: 95%: {pp_values['95']}pp, 98%: {pp_values['98']}pp, 99%: {pp_values['99']}pp, 100%: {pp_values['100']}pp"
        )