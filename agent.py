import os
import json
from dotenv import load_dotenv
import anthropic
from spotify_tools import search_tracks_batch, create_playlist
from lastfm_tools import get_similar_artists, get_top_tracks

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


tools = [
    {
        "name": "get_similar_artists",
        "description": "Finds artists that are similar to the given artist",
        "input_schema": {
            "type": "object",
            "properties": {
                "artist": {
                    "type": "string",
                    "description": "Name of the given artist"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of similar artists, default 5"
                }
            },
            "required": ["artist"]
        }
    },
    {
        "name": "get_top_tracks",
        "description": "Finds the top tracks of a given artist",
        "input_schema": {
            "type": "object",
            "properties": {
                "artist": {
                    "type": "string",
                    "description": "Name of the given artist",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of tracks, default is 10",
                }
            },
            "required": ["artist"]
        }
    },
    ##### Had to change to batch processing to save on tokens; this was the initial tool I used
    # {
    #     "name": "search_tracks",
    #     "description": "Searches for a track on Spotify and returns its Spotify track ID. Use this to find the Spotify ID for a specific track and artist combination.",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": {
    #             "query": {
    #                 "type": "string",
    #                 "description": "Search query that contains tracks",
    #             },
    #             "limit": {
    #                 "type": "integer",
    #                 "description": "Number of tracks, default 10"
    #             }
    #         },
    #         "required": ["query"]
    #     }
    # },
    {
    "name": "search_tracks_batch",
    "description": "Searches Spotify IDs for a list of tracks at once. Use this instead of search_tracks to find IDs for multiple tracks in a single call.",
    "input_schema": {
        "type": "object",
        "properties": {
            "tracks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "artist": {"type": "string"}
                    }
                },
                "description": "List of tracks with name and artist"
            }
        },
        "required": ["tracks"]
    }
},
    {
        "name": "create_playlist",
        "description": "Creates a playlist. Use this as the final step once all track IDs have been collected.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the created playlist",
                },
                "track_ids": {
                    "type": "array",
                    "description": "List of track IDs to put into the playlist"
                } 
            }, 
            "required": ["name", "track_ids"]
        }
    }
]

sys_prompt = """
You are a playlist agent, a curator of music. Your task is to create personalised playlists on spotify, based on user input.
The input might be an artist and you would need to find similar artists and put together a playlist of their tracks.
It migh be a genre or a mood, and your task would be to find songs that fit those. 

An example could look like this:
'Agent, make me a playlist too which I can enjoy my coffee in the morning, after waking up.'
Then you could choose something calm or vibey, a classic would be Jazz or jazzy beats.

Another example could be: 
'I feel like dancing today.'
You could then choose tracks that are danceable, like EDM or Salsa, depending on the user.

You have access to the following tools:
- get_similar_artists: use this to find artists similar to a given artist
- get_top_tracks: use this to find the top tracks of an artist
- search_tracks_batch: use this to find the Spotify ID of a batch of specific tracks. use this ONCE with all tracks at the same time to find their Spotify IDs. Do not call this tool multiple times.
- create_playlist: use this as the final step to create the playlist

Follow these steps:
1. Interpret the user's request and identify a starting artist or genre
2. If the user's request is too vague to identify a starting artist or genre, 
ask a clarifying question before using any tools. 
3. If the user mentions an artist, use them as the starting point. 
If not, identify a fitting artist yourself based on the mood or genre.
4. If everything is clear, start looking for similar artists on last.fm.
5. Once you have found similar artists, find for their top tracks on last.fm.
6. When you have found our the names of their top tracks, find their track ids on spotify.
7. When you have found those, create the playlist. Give it a fitting name.
8. Once the playlist is created, tell the user the playlist name 
and share the Spotify link.
"""

def execute_tool(tool_name: str, tool_input: dict):
    tool_map = {
        "get_similar_artists": get_similar_artists,
        "get_top_tracks": get_top_tracks,
        "search_tracks_batch": search_tracks_batch,
        "create_playlist": create_playlist
    }
    tool = tool_map[tool_name]
    result = tool(**tool_input)
    print(f">> Result: {result}")
    return result

def run_agent(user_message):
    messages = [{"role": "user", "content": user_message}]
    
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=sys_prompt,
            tools=tools,
            messages=messages
        )
        
        if response.stop_reason == "end_turn":
            final = next(b for b in response.content if b.type == "text")
            print(f"\nAgent: {final.text}")
            break
        
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n>> Tool: {block.name}({block.input})")
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })
            
            messages.append({"role": "user", "content": tool_results})

if __name__ == "__main__":
    user_input = input("Was für eine Playlist soll ich erstellen? ")
    run_agent(user_input)

