# Spotify_Playlist_Agent
AI Agent that creates a Spotify playlist based on user input.

The agent can use 4 tools: finding similar artists, finding an artists top tracks, searching track ids and creating a playlist.
The idea is to have the agent choose a starting point based on the user prompt, which can be very specific or vague. If necessary, the agent is instructed to ask follow-up questions until the request is clear enough.

The starting point then would be an artist that fits the user input, and from there the agent can use the given tools to curate a list of tracks. This is done in the last.fm API, since Spotify heavily cut their API endpoints in 2025.
Those curated tracks are then searched in spotify and put into a playlist.

## Work in progress
Next steps:
- reduce token usage
- local implementation using Ollama for example
- possibly expanding to other streaming services where possible
- making track selection a bit more sophisticated

## Tech Stack
- Anthropic Claude claude-sonnet-4-20250514 (Anthropic SDK)
- Spotify Web API (spotipy)
- Last.fm API

## Setup
1. Clone the repo
2. pip install -r requirements.txt
3. Add credentials to .env (see .env.example)
4. python agent.py

## Example
> "Make me a creative Cool Jazz playlist, not the absolute classics, around 20 tracks."

The agent identifies Chet Baker as a starting point, finds similar artists via Last.fm, 
collects their top tracks, searches Spotify IDs, and creates a playlist – all autonomously.
