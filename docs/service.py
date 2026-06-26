import requests
from flask import current_app

class LogisticsService:
    """
    Servizio per la gestione del routing, distance matrix e geocoding
    utilizzando OpenRouteService (Livello 1 - Gratuito).
    """
    def __init__(self, api_key=None):
        self.api_key = api_key or current_app.config.get('OPENROUTESERVICE_API_KEY')
        self.base_url = "https://api.openrouteservice.org"

    def _get_headers(self):
        return {
            "Authorization": self.api_key,
            "Content-Type": "application/json; charset=utf-8"
        }

    def get_directions(self, start_coords, end_coords, profile='driving-car'):
        """Calcola il percorso tra due punti (A -> B)."""
        url = f"{self.base_url}/v2/directions/{profile}"
        body = {
            "coordinates": [start_coords, end_coords]
        }
        response = requests.post(url, json=body, headers=self._get_headers())
        response.raise_for_status()
        data = response.json()
        
        # Estraiamo i dati principali: distanza (m) e durata (s)
        summary = data['routes'][0]['summary']
        return {
            "distance": summary['distance'],
            "duration": summary['duration'],
            "geometry": data['routes'][0]['geometry']
        }

    def get_matrix(self, locations, profile='driving-car', metrics=['distance', 'duration']):
        """Calcola la matrice di distanze tra molteplici punti."""
        url = f"{self.base_url}/v2/matrix/{profile}"
        body = {
            "locations": locations,
            "metrics": metrics
        }
        response = requests.post(url, json=body, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def geocode(self, text, limit=1):
        """Converte un indirizzo testuale in coordinate (Lat/Lng)."""
        url = f"{self.base_url}/geocode/search"
        params = {
            "api_key": self.api_key,
            "text": text,
            "size": limit
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data['features']:
            return None
            
        feature = data['features'][0]
        return {
            "label": feature['properties']['label'],
            "coordinates": feature['geometry']['coordinates'] # [lng, lat]
        }