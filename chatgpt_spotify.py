
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

# This file in my new branch

load_dotenv()   # Import environment variables from .env file
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_ID = os.getenv("SPOTIFY_USER_ID")
REDIRECT_URI = "http://localhost:8888/callback"
print(f"My Spotify User ID = {USER_ID}")
# Scopes required for the program
SCOPES = "user-read-playback-state user-modify-playback-state user-read-private"

def authenticate_spotify():
    """
    Authenticates the user and returns a Spotipy client object.
    """
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES
    ))
    return sp

def search_track(sp, artist_name, track_name):
    """
    Searches for a track on Spotify using the artist name and track title.
    """
    query = f"artist:{artist_name} track:{track_name}"
    results = sp.search(q=query, type="track", limit=1)
    if results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        print(f"Found track: {track['name']} by {track['artists'][0]['name']}")
        return track["id"]
    else:
        print("Track not found!")
        return None

def play_track(sp, track_id):

    # Plays the specified track on the user's active device.
    devices = sp.devices()
    # Print all devices for debugging
    for device in devices['devices']:
        print(f"Name: {device['name']}, ID: {device['id']}, Active: {device['is_active']}")
        my_device_id = device['id']

    if devices["devices"]:
        active_device = devices["devices"][0]
        print(f"Playing on device: {active_device['name']}")
        sp.start_playback(device_id=my_device_id, uris=[f"spotify:track:{track_id}"])
    else:
        print("No active devices found. Please open Spotify on one of your devices.")

def main():
    # Step 1: Authenticate and get the Spotipy client
    sp = authenticate_spotify()

    # Step 2: Get user input for artist and song title
    artist_name = input("Enter artist name: ")
    track_name = input("Enter song title: ")

    # Step 3: Search for the track
    track_id = search_track(sp, artist_name, track_name)
    print(track_id)
    if track_id:
        # Step 4: Play the track
        play_track(sp, track_id)

if __name__ == "__main__":
    main()

