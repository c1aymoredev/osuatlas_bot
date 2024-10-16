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
        
    def handle_help_command(self) -> str:
        return " | ".join([
            "Available commands:",
            "!pp <map_id> [mods] - Calculate PP for a map",
            "!stats <username> - Show user statistics",
            "!compare <username1> <username2> - Compare two users",
            "!fc [username] - Calculate FC PP for user's last play",
            "!with <mods> - Recalculate PP with different mods for the last map",
            "!r [params] - Get a map recommendation",
            "!notifyme <twitch_username> - Get notified when a Twitch streamer goes live",
            "!help - Show this help message"
        ])

    def handle_pp_command(self, message: str, sender: str) -> str:
        parts = message.split()
        if len(parts) < 2:
            return "Usage: !pp <map_id> [mods]"
        
        map_id = parts[1]
        mods_str = ' '.join(parts[2:]) if len(parts) > 2 else 'NM'
        
        try:
            mods = parse_mods(mods_str.split())
            beatmap_path = self.api_client.download_map(map_id)
            map_info = self.api_client.get_map_info(map_id)
            pp_values, stars, ar, od, cs, hp = self.pp_calculator.calculate_pp(beatmap_path, mods)
            
            self.bot.last_map[sender] = {'id': map_id, 'mods': mods}
            
            return self.pp_calculator.format_pp_result(map_info, pp_values, stars, ar, od, cs, hp, mods)
        except ValueError as e:
            return f"Error: {str(e)}"
        except ConnectionError as e:
            return f"Error downloading map: {str(e)}"
        except Exception as e:
            return f"An unknown error occurred: {str(e)}"

    def handle_with_command(self, message: str, sender: str) -> str:
        if sender not in self.bot.last_map:
            return "First use the !pp, !fc or /np command to select a map."
        
        parts = message.split()
        if len(parts) < 2:
            return "Please specify mods. Example: !with HDDT"
        
        new_mods = ' '.join(parts[1:])
        map_id = self.bot.last_map[sender]['id']
        
        return self.handle_pp_command(f"!pp {map_id} {new_mods}", sender)

    def handle_recommendation_command(self, message: str, sender: str) -> str:
        params = message.split()[1:]
        return self.recommender.get_recommendation(sender, params)
    
    def handle_notifyme_command(self, message: str, sender: str) -> str:
        parts = message.split()
        if len(parts) != 2:
            return "Usage: !notifyme <twitch_username>"
        
        twitch_username = parts[1]
        if self.bot.twitch_integration.subscribe_to_stream(sender, twitch_username):
            return f"You will be notified when {twitch_username} starts streaming."
        else:
            return f"Failed to subscribe to {twitch_username}. Please check the username and try again."
    
    def handle_stats_command(self, message: str) -> str:
        parts = message.split()
        if len(parts) != 2:
            return "Usage: !stats <username>"
        
        username = parts[1]
        try:
            stats = self.api_client.get_user_stats(username)
            
            def format_number(num):
                try:
                    return f"{int(float(num)):,}".replace(',', ' ')
                except ValueError:
                    return "N/A"

            def safe_get(key, default="N/A"):
                return stats.get(key, default)

            def safe_float(value, default=0.0):
                try:
                    return float(value)
                except ValueError:
                    return default

            count300 = int(safe_get('count300', 0))
            count100 = int(safe_get('count100', 0))
            count50 = int(safe_get('count50', 0))
            countmiss = int(safe_get('countmiss', 0))
            total_hits = count300 + count100 + count50
            total_plays = total_hits + countmiss
            hit_percent = (total_hits / total_plays) * 100 if total_plays > 0 else 0

            return " | ".join([
                f"Stats for {safe_get('username')} (https://osu.ppy.sh/users/{safe_get('user_id')})",
                f"Rank: #{format_number(safe_get('pp_rank'))} (#{safe_get('pp_country_rank')} {safe_get('country')})",
                f"Performance: {safe_float(safe_get('pp_raw')):.2f}pp",
                f"Accuracy: {safe_float(safe_get('accuracy')):.2f}%",
                f"Level: {safe_float(safe_get('level')):.2f}",
                f"Play Count: {format_number(safe_get('playcount'))}",
                f"Total Score: {format_number(safe_get('total_score'))}",
                f"Hit Accuracy: {hit_percent:.2f}%",
                f"Total Hits: {format_number(total_hits)}",
                f"Maximum Combo: {format_number(safe_get('max_combo'))}",
                f"Top Ranks: SS+: {safe_get('count_rank_ssh')} | SS: {safe_get('count_rank_ss')} | S+: {safe_get('count_rank_sh')} | S: {safe_get('count_rank_s')} | A: {safe_get('count_rank_a')}",
                f"Hit Counts: 300: {format_number(count300)} | 100: {format_number(count100)} | 50: {format_number(count50)}"
            ])
        except ValueError as e:
            return str(e)
        except ConnectionError as e:
            return f"Error fetching stats: {str(e)}"

    def handle_compare_command(self, message: str) -> str:
        parts = message.split()
        if len(parts) != 3:
            return "Usage: !compare <username1> <username2>"
        
        username1, username2 = parts[1], parts[2]
        try:
            stats1 = self.api_client.get_user_stats(username1)
            stats2 = self.api_client.get_user_stats(username2)

            def safe_get(stats, key, default=0):
                return stats.get(key, default)

            def safe_convert(value, convert, default=0):
                try:
                    return convert(value)
                except ValueError:
                    return default

            comparisons = [
                ('Rank', 'pp_rank', int, False),
                ('PP', 'pp_raw', float, True),
                ('Accuracy', 'accuracy', float, True),
                ('Level', 'level', float, True),
                ('Play Count', 'playcount', int, True),
                ('Total Score', 'total_score', int, True),
                ('SS+ Count', 'count_rank_ssh', int, True),
                ('SS Count', 'count_rank_ss', int, True),
                ('S+ Count', 'count_rank_sh', int, True),
                ('S Count', 'count_rank_s', int, True),
                ('A Count', 'count_rank_a', int, True)
            ]

            result = f"Comparison between {stats1['username']} and {stats2['username']}:\n\n"
            for name, key, convert, higher_better in comparisons:
                val1 = safe_convert(safe_get(stats1, key), convert)
                val2 = safe_convert(safe_get(stats2, key), convert)
                if key == 'accuracy':
                    val1, val2 = round(val1, 2), round(val2, 2)
                result += f"{name}: {val1:,} vs {val2:,} "
                if val1 != val2:
                    better = max if higher_better else min
                    winner = stats1['username'] if better(val1, val2) == val1 else stats2['username']
                    result += f"({winner} is better)"
                result += "\n"

            return result

        except ValueError as e:
            return str(e)
        except ConnectionError as e:
            return f"Error fetching stats: {str(e)}"
        
    def handle_fc_command(self, message: str, sender: str) -> str:
        parts = message.split()
        if len(parts) == 1:
            username = sender
        elif len(parts) == 2:
            username = parts[1]
        else:
            return "Usage: !fc [username]"
        
        try:
            last_play = self.api_client.get_last_play(username)
            beatmap_id = last_play['beatmap_id']
            
            beatmap_path = self.api_client.download_map(beatmap_id)
            
            beatmap_info = self.api_client.get_map_info(beatmap_id)
            
            count300 = int(last_play['count300'])
            count100 = int(last_play['count100'])
            count50 = int(last_play['count50'])
            countmiss = int(last_play['countmiss'])
            total_hits = count300 + count100 + count50 + countmiss
            current_acc = (count300 * 300 + count100 * 100 + count50 * 50) / (total_hits * 300) * 100

            fc_300s = count300 + countmiss
            fc_acc = (fc_300s * 300 + count100 * 100 + count50 * 50) / ((total_hits) * 300) * 100

            mods = int(last_play['enabled_mods'])

            fc_pp = self.pp_calculator.calculate_fc_pp(beatmap_path, mods, fc_acc, int(beatmap_info['max_combo']))

            current_pp = self.pp_calculator.calculate_fc_pp(beatmap_path, mods, current_acc, int(last_play['maxcombo']))

            self.bot.last_map[sender] = {'id': beatmap_id, 'mods': mods}

            return (
                f"FC Estimate for {username}'s last play:\n"
                f"▸ Map: {beatmap_info['artist']} - {beatmap_info['title']} [{beatmap_info['version']}]\n"
                f"▸ Current: {current_pp:.2f}PP ({current_acc:.2f}% | {last_play['maxcombo']}/{beatmap_info['max_combo']}x | {countmiss} misses)\n"
                f"▸ If FC: {fc_pp:.2f}PP ({fc_acc:.2f}%)\n"
                f"▸ Difference: +{fc_pp - current_pp:.2f}PP"
            )
        except ValueError as e:
            return str(e)
        except ConnectionError as e:
            return f"Error fetching data: {str(e)}"