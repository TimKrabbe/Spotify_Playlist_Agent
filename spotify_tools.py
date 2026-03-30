import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="playlist-modify-public playlist-modify-private"
))

def search_tracks(query: str, limit: int = 10) -> list[dict]:
    """Sucht nach Tracks auf Spotify und gibt relevante Felder zurück."""
    results = sp.search(q=query, type="track", limit=limit)
    tracks = []
    for item in results["tracks"]["items"]:
        tracks.append({
            "id": item["id"],
            "name": item["name"],
            "artist": item["artists"][0]["name"],
            "popularity": item.get("popularity")
        })
    return tracks

def search_tracks_batch(tracks: list[dict]) -> list[str]:
    """Sucht Spotify IDs für eine Liste von {name, artist} Dictionaries."""
    track_ids = []
    for track in tracks:
        query = f"{track['name']} {track['artist']}"
        results = search_tracks(query, limit=1)
        if results and results[0]["id"]:
            track_ids.append(results[0]["id"])
    return track_ids

### deprecated endpoint :(
# def get_recommendations(
#     seed_tracks: list[str] = None,
#     seed_genres: list[str] = None,
#     seed_artists: list[str] = None,
#     limit: int = 20,
#     target_energy: float = None,
#     target_valence: float = None,
#     target_tempo: float = None
# ) -> list[dict]:
#     """Holt Empfehlungen basierend auf Seeds und optionalen Audio-Feature-Targets."""
#     kwargs = {
#         "seed_tracks": seed_tracks or [],
#         "seed_genres": seed_genres or [],
#         "seed_artists": seed_artists or [],
#         "limit": limit
#     }
#     # Nur mitschicken wenn explizit gesetzt (None = kein Filter)
#     if target_energy is not None:
#         kwargs["target_energy"] = target_energy
#     if target_valence is not None:
#         kwargs["target_valence"] = target_valence
#     if target_tempo is not None:
#         kwargs["target_tempo"] = target_tempo

#     results = sp.recommendations(**kwargs)
#     tracks = []
#     for item in results["tracks"]:
#         tracks.append({
#             "id": item["id"],
#             "name": item["name"],
#             "artist": item["artists"][0]["name"],
#             "popularity": item["popularity"]
#         })
#     return tracks


def create_playlist(name: str, track_ids: list[str]) -> str:
    playlist = sp.current_user_playlist_create(name=name, public=False)
    sp.playlist_add_items(playlist_id=playlist["id"], items=track_ids)
    return playlist["external_urls"]["spotify"]



# if __name__ == "__main__":
#     # Test 1: Suche
#     results = search_tracks("Bonobo")
#     print("Suchergebnisse:")
#     for t in results[:3]:
#         print(f"  {t['name']} – {t['artist']}")

    # # Test 2: Empfehlungen basierend auf dem ersten Ergebnis
    # recs = get_recommendations(
    #     seed_tracks=[results[0]["id"]],
    #     target_energy=0.4,
    #     target_valence=0.3
    # )
    # print("\nEmpfehlungen:")
    # for t in recs[:5]:
    #     print(f"  {t['name']} – {t['artist']}")