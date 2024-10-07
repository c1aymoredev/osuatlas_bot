import json
import requests
import time
import os
from typing import Dict, Any, List
from config import OSU_API_KEY, REQUEST_INTERVAL, MAPS_DIRECTORY, RECOMMENDATIONS_DIRECTORY


class OsuAPIClient:
    def __init__(self):
        self.api_key = OSU_API_KEY
        self.last_request_time = 0

    def rate_limited_request(self, url: str, params: Dict[str, Any] = None) -> requests.Response:
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < REQUEST_INTERVAL:
            time.sleep(REQUEST_INTERVAL - time_since_last_request)
        
        response = requests.get(url, params=params)
        self.last_request_time = time.time()
        return response

    def get_map_info(self, map_id: str) -> Dict[str, Any]:
        url = f"https://osu.ppy.sh/api/get_beatmaps"
        params = {
            'k': self.api_key,
            'b': map_id
        }
        response = self.rate_limited_request(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]  # API возвращает список, нам нужен первый элемент
            else:
                raise ValueError("Map not found")
        else:
            raise ConnectionError(f"Failed to get map info. Status code: {response.status_code}")

    def download_map(self, map_id: str) -> str:
        file_path = os.path.join(MAPS_DIRECTORY, f"{map_id}.osu")
        if not os.path.exists(file_path):
            url = f"https://osu.ppy.sh/osu/{map_id}"
            response = self.rate_limited_request(url)
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
            else:
                raise ConnectionError("Failed to download .osu file")
        return file_path

    def get_user_top_scores(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        url = f"https://osu.ppy.sh/api/get_user_best?k={OSU_API_KEY}&u={username}&m=0&limit={limit}"
        response = self.rate_limited_request(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data
            else:
                raise ValueError("Player not found or no scores available.")
        else:
            raise ConnectionError(f"Failed to retrieve user information. Status code: {response.status_code}")

    def calculate_average_pp(self, top_scores: List[Dict[str, Any]]) -> float:
        if not top_scores:
            return 0
        
        total_pp = sum(float(score['pp']) for score in top_scores)
        return total_pp / len(top_scores)

    def load_map_recommendations(self) -> List[Dict[str, Any]]:
        recommendations = []
        for filename in os.listdir(RECOMMENDATIONS_DIRECTORY):
            if filename.endswith(".json"):
                with open(os.path.join(RECOMMENDATIONS_DIRECTORY, filename), "r") as f:
                    recommendations.extend(json.load(f))
        return recommendations