import os
import requests
from dotenv import load_dotenv

print(os.getcwd())

load_dotenv()
API_KEY = os.getenv("LASTFM_API_KEY")

headers = {"User-Agent": "playlist-agent/1.0"}

def get_similar_artists(artist, limit):
    response = requests.get("https://ws.audioscrobbler.com/2.0/", 
                            headers = headers,
                            params={
                                "method": "artist.getSimilar",
                                "artist": artist,
                                "autocorrect": 1,
                                "limit": limit,
                                "format": "json",
                                "api_key": API_KEY,
                            })
    data = response.json()
    if "error" in data:
        return []

    artists = data["similarartists"]["artist"]

    return [a["name"] for a in artists]


def get_top_tracks(artist, limit):
    response = requests.get("https://ws.audioscrobbler.com/2.0/",
                            headers = headers,
                            params = {
                                "method": "artist.getTopTracks",
                                "artist": artist,
                                "autocorrect": 1,
                                "limit": limit,
                                "format": "json",
                                "api_key": API_KEY,
                            })
    data = response.json()

    tracks = data["toptracks"]["track"]

    return [{"name": t["name"], "artist": artist} for t in tracks]

def search_track(track, artist):
    response = requests.get("https://ws.audioscrobbler.com/2.0/",
                            headers = headers,
                            params = {
                                "method": "track.search",
                                "track": track,
                                "artist": artist,
                                "limit": 1,
                                "format": "json",
                                "api_key": API_KEY,                                
                            })
    data = response.json()
    if "error" in data:
        return []
    url = data["results"]["trackmatches"]["track"][0].get("url")
    return url


# if __name__ == "__main__":
#     similar = get_similar_artists("Bad Bunny", 3)
#     for s in similar:
#         print(f"Name: {s}")

    
#     top_tracks = [{"artist": s, "top_tracks": get_top_tracks(s, 5)} for s in similar]
#     for t in top_tracks:
#         print(t) 

#     for t in top_tracks:
#         for track in t["top_tracks"]:
#             urls = search_track(track["name"], t["artist"])
#             print(urls)


