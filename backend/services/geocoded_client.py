"""
Client per l'API geocoded.me (https://geocoded.me).
Free, no API key, no rate limits. 230.000+ città, 252 paesi.
Dati: GeoNames + Wikidata (CC BY 4.0).
"""
import requests
from flask import current_app


class GeocodedClient:
    BASE_URL = "https://api.geocoded.me"

    def _get_url(self):
        try:
            return current_app.config.get("GEOCODED_ME_BASE_URL", self.BASE_URL)
        except RuntimeError:
            return self.BASE_URL

    def get_states(self, country="IT", limit=200):
        url = f"{self._get_url()}/countries/{country}/states"
        params = {"limit": limit, "fields": "name,iso2,latitude,longitude,type"}
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])

    def get_cities(self, country, state_code, limit=500):
        url = f"{self._get_url()}/countries/{country}/states/{state_code}/cities"
        params = {"limit": limit, "fields": "name,latitude,longitude,population"}
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", []), data.get("meta", {}).get("hasMore", False)

    def get_all_cities(self, country, state_code):
        all_cities = []
        cursor = None
        limit = 500
        while True:
            url = f"{self._get_url()}/countries/{country}/states/{state_code}/cities"
            params = {"limit": limit, "fields": "name,latitude,longitude,population"}
            if cursor:
                params["cursor"] = cursor
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            all_cities.extend(data.get("data", []))
            meta = data.get("meta", {})
            if meta.get("hasMore"):
                cursor = meta.get("cursor")
            else:
                break
        return all_cities

    def search_cities(self, country, query, limit=20):
        url = f"{self._get_url()}/countries/{country}/cities"
        params = {"limit": limit, "query": query, "fields": "name,latitude,longitude,population"}
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])


geocoded_client = GeocodedClient()
