# Branch: gary-readJSON
from enum import global_enum_repr

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import json
import textwrap
from rich import print
from rich.console import Console
# from gtts import gTTS
# import requests

load_dotenv()   # Import environment variables from .env file
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_ID = os.getenv("SPOTIFY_USER_ID")
REDIRECT_URI = "http://localhost:8888/callback"
# print(f"My Spotify User ID = {USER_ID}")
print()
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
        print(track)
        return track["id"]
    else:
        print("Track not found!")
        return None

def play_track(sp, track_id):

    # Plays the specified track on the user's active device.
    devices = sp.devices()
    # Print all devices for debugging
    my_device_id = None
    for device in devices['devices']:
        # print(f"Name: {device['name']}, ID: {device['id']}, Active: {device['is_active']}")
        my_device_id = device['id']

    if devices["devices"]:
        # print(f"Playing on device: {active_device['name']}")
        sp.start_playback(device_id=my_device_id, uris=[f"spotify:track:{track_id}"])
    else:
        print("No active devices found. Please open Spotify on one of your devices.")

def print_track_description(all_songs, genre, song_index):

    # Print out the top header
    console = Console(width=60)
    print()
    console.rule("[bold red]Description Start")
    print()

    # Print out the track description
    wrapped_text = textwrap.fill(all_songs[genre][song_index]['description'], width=50)
    console.print(wrapped_text, justify="center")
    print()

    # Print out the bottom header
    console.rule("[bold red]Description End")
    print()

def main():
    # Step 1: Authenticate and get the Spotipy client
    sp = authenticate_spotify()

    # Pick a decade for your music playlist

    # View the list of songs by genre in your chosen decade
    # and choose the genre you want to listen to



    # initial_setup of json
    file_name = '1960s.json'
    decade = file_name[:5]
    # Was getting error with ' char, needed to set this encoding
    with open(file_name, 'r', encoding="utf-8") as f:
        all_songs = json.load(f)
    genre = "country"
    for song in all_songs[genre]:
        artist_name = song["artist"]
        track_name = song["song_name"]
        print()
        print(f"   Genre: {genre:<5}  {decade:<5}   Rank # {song['rank']}   Released in {song['year']:<2}")
        print()
        print(f"   Artist: {artist_name}    Song: {track_name}")
        print_track_description(all_songs, genre, song["rank"]-1)

        input("Press Enter to Start Playing Track . . .")
        print()

        track_id = search_track(sp, artist_name, track_name)
        play_track(sp, track_id)
        input("Press Enter to Go On to next Track. . .")
        print()

if __name__ == "__main__":
    main()

