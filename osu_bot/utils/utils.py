from typing import List, Dict
from config import MODS

def parse_mods(mod_strings: List[str]) -> int:
    if not mod_strings or mod_strings == ['NoMod'] or mod_strings == ['NM']:
        return 0
    
    mods = 0
    mod_mapping = {
        'EZ': 'Easy', 'NF': 'NoFail', 'HT': 'HalfTime', 'HR': 'HardRock',
        'SD': 'SuddenDeath', 'DT': 'DoubleTime', 'NC': 'Nightcore',
        'HD': 'Hidden', 'FL': 'Flashlight', 'SO': 'SpunOut',
        'AP': 'Autopilot', 'PF': 'Perfect'
    }
    
    reverse_mod_mapping = {v.lower(): k for k, v in mod_mapping.items()}
    
    for mod in mod_strings:
        mod = mod.strip().lstrip('+-')
        mod_lower = mod.lower()
        
        if len(mod) > 2:
            for i in range(0, len(mod), 2):
                sub_mod = mod[i:i+2].upper()
                if sub_mod in MODS:
                    mods |= MODS[sub_mod]['mask']
                else:
                    raise ValueError(f"Unknown mod: {sub_mod}")
        elif mod.upper() in MODS:
            mods |= MODS[mod.upper()]['mask']
        elif mod_lower in reverse_mod_mapping:
            short_mod = reverse_mod_mapping[mod_lower]
            mods |= MODS[short_mod]['mask']
        else:
            raise ValueError(f"Unknown mod: {mod}")
    
    return mods

def mods_to_string(mods: int) -> str:
    if mods == 0:
        return "NoMod"
    mod_string = ""
    for mod, info in MODS.items():
        if mods & info['mask']:
            mod_string += mod
    return mod_string

def mods_to_int(mods_string: str) -> int:
    mods_int = 0
    if isinstance(mods_string, str):
        for i in range(0, len(mods_string), 2):
            mod = mods_string[i:i+2]
            if mod in MODS:
                mods_int |= MODS[mod]['mask']
    return mods_int

def calculate_bpm(base_bpm: float, mods: int) -> int:
    if mods & (MODS['DT']['mask'] | MODS['NC']['mask']):
        return round(base_bpm * 1.5)
    elif mods & MODS['HT']['mask']:
        return round(base_bpm * 0.75)
    return round(base_bpm)

def apply_mods_to_difficulty(difficulty: float, mods: int) -> float:
    if mods & (MODS['DT']['mask'] | MODS['NC']['mask']):
        difficulty *= 1.4
    if mods & MODS['HT']['mask']:
        difficulty *= 0.5
    if mods & MODS['HR']['mask']:
        difficulty *= 1.1
    if mods & MODS['EZ']['mask']:
        difficulty *= 0.5
    return difficulty

def apply_mods_to_stats(stats: Dict[str, float], mods: int) -> Dict[str, float]:
    modified_stats = stats.copy()
    if mods & (MODS['DT']['mask'] | MODS['NC']['mask']):
        modified_stats["AR"] = ar_to_ms(stats["AR"])
        modified_stats["AR"] = ms_to_ar(modified_stats["AR"] * 2/3)
        modified_stats["OD"] = od_to_ms(stats["OD"])
        modified_stats["OD"] = ms_to_od(modified_stats["OD"] * 2/3)
        modified_stats["BPM"] *= 1.5
    if mods & MODS['HT']['mask']:
        modified_stats["AR"] = ar_to_ms(stats["AR"])
        modified_stats["AR"] = ms_to_ar(modified_stats["AR"] * 4/3)
        modified_stats["OD"] = od_to_ms(stats["OD"])
        modified_stats["OD"] = ms_to_od(modified_stats["OD"] * 4/3)
        modified_stats["BPM"] *= 0.75
    if mods & MODS['HR']['mask']:
        modified_stats["AR"] = min(stats["AR"] * 1.4, 10)
        modified_stats["OD"] = min(stats["OD"] * 1.4, 10)
        modified_stats["CS"] = min(stats["CS"] * 1.3, 10)
        modified_stats["HP"] = min(stats["HP"] * 1.4, 10)
    if mods & MODS['EZ']['mask']:
        modified_stats["AR"] *= 0.5
        modified_stats["OD"] *= 0.5
        modified_stats["CS"] *= 0.5
        modified_stats["HP"] *= 0.5
    return modified_stats

def ar_to_ms(ar: float) -> float:
    if ar <= 5:
        return 1800 - 120 * ar
    return 1200 - 150 * (ar - 5)

def ms_to_ar(ms: float) -> float:
    if ms >= 1200:
        return (1800 - ms) / 120
    return 5 + (1200 - ms) / 150

def od_to_ms(od: float) -> float:
    return 80 - 6 * od

def ms_to_od(ms: float) -> float:
    return (80 - ms) / 6

class UserException(Exception):
    pass