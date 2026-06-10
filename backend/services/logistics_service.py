"""
Logistics Service — routing, distance matrix e geocoding.
Usa OpenRouteService (Livello 1 gratuito) con fallback Haversine.
"""

import math
import json
from urllib.request import Request, urlopen
from flask import current_app


class LogisticsService:
    ORS_BASE_URL = "https://api.openrouteservice.org"

    def __init__(self, api_key=None):
        self.api_key = api_key

    def _resolve_key(self):
        if self.api_key:
            return self.api_key
        try:
            return current_app.config.get("OPENROUTESERVICE_API_KEY", "")
        except RuntimeError:
            return ""

    def _haversine(self, lon1, lat1, lon2, lat2):
        R = 6371000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        )
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _urllib_json(self, url, data=None, headers=None, method=None, timeout=15):
        if headers is None:
            headers = {}
        body = json.dumps(data).encode() if data else None
        req = Request(url, data=body, headers=headers, method=method)
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())

    def get_directions(self, start_coords, end_coords, profile="driving-car"):
        key = self._resolve_key()
        if key:
            return self._ors_directions(start_coords, end_coords, profile, key)
        return self._fallback_directions(start_coords, end_coords)

    def _ors_directions(self, start, end, profile, key):
        url = f"{self.ORS_BASE_URL}/v2/directions/{profile}"
        body = {"coordinates": [start, end]}
        headers = {
            "Authorization": key,
            "Content-Type": "application/json; charset=utf-8",
        }
        data = self._urllib_json(
            url, data=body, headers=headers, method="POST", timeout=15
        )
        summary = data["routes"][0]["summary"]
        return {
            "distance": summary["distance"],
            "duration": summary["duration"],
            "geometry": data["routes"][0].get("geometry"),
            "provider": "openrouteservice",
        }

    def _fallback_directions(self, start, end):
        distance = self._haversine(start[0], start[1], end[0], end[1])
        duration = distance / 13.9
        return {
            "distance": round(distance, 2),
            "duration": round(duration, 2),
            "geometry": None,
            "provider": "haversine",
        }

    def get_matrix(self, locations, profile="driving-car", metrics=None):
        if metrics is None:
            metrics = ["distance", "duration"]
        key = self._resolve_key()
        if key:
            return self._ors_matrix(locations, profile, metrics, key)
        return self._fallback_matrix(locations)

    def _ors_matrix(self, locations, profile, metrics, key):
        url = f"{self.ORS_BASE_URL}/v2/matrix/{profile}"
        body = {"locations": locations, "metrics": metrics}
        headers = {
            "Authorization": key,
            "Content-Type": "application/json; charset=utf-8",
        }
        return self._urllib_json(
            url, data=body, headers=headers, method="POST", timeout=30
        )

    def _fallback_matrix(self, locations):
        n = len(locations)
        distances = [[0] * n for _ in range(n)]
        durations = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    d = self._haversine(
                        locations[i][0],
                        locations[i][1],
                        locations[j][0],
                        locations[j][1],
                    )
                    distances[i][j] = round(d, 2)
                    durations[i][j] = round(d / 13.9, 2)
        return {"distances": distances, "durations": durations, "provider": "haversine"}

    def geocode(self, text, limit=1):
        key = self._resolve_key()
        if key:
            return self._ors_geocode(text, limit, key)
        return None

    def _ors_geocode(self, text, limit, key):
        from urllib.parse import urlencode

        url = f"{self.ORS_BASE_URL}/geocode/search?{urlencode({'api_key': key, 'text': text, 'size': limit})}"
        data = self._urllib_json(url, timeout=15)
        if not data.get("features"):
            return None
        f = data["features"][0]
        return {
            "label": f["properties"]["label"],
            "coordinates": f["geometry"]["coordinates"],
        }
