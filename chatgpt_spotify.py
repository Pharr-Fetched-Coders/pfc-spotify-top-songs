# Branch: gary-readJSON
# from enum import global_enum_repr
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import json
from gtts import gTTS
import textwrap
from rich import print
from rich.console import Console
from playsound3 import playsound
import pyfiglet
import time
import threading
import keyboard
import sys
import random

load_dotenv()   # Import environment variables from .env file
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_ID = os.getenv("SPOTIFY_USER_ID")
REDIRECT_URI = "http://localhost:8888/callback"
# print(f"My Spotify User ID = {USER_ID}")
print()
# Scopes required for the program
SCOPES = "user-read-playback-state user-modify-playback-state user-read-private"

break_sleep = False
skip_speech = True

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
        # print(track)

        return track["id"], track["duration_ms"]
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

    return my_device_id

def print_track_description(all_songs, genre, song_index):
    # Print out the top header
    console = Console(width=60)
    print()
    console.rule("[bold red]Description Start")
    print()

    pyfiglet_text = pyfiglet.figlet_format(f"{song_index+1}  {all_songs[genre][song_index]['artist']}")
    print(pyfiglet_text)

    # Print out the track description
    wrapped_text = textwrap.fill(all_songs[genre][song_index]['description'], width=60)
    console.print(wrapped_text, justify="center")
    print()

    # Print out the bottom header
    console.rule("[bold red]Description End")
    print()


    # input('Press Enter to Play Description . . .')
    # Create a speech file of description

    # Remove the previous speech file if it exists
    if os.path.exists("speech.mp3"):
        os.remove("speech.mp3")


    if not skip_speech:
        tts = gTTS(all_songs[genre][song_index]['description'])
        tts.save("speech.mp3")
        playsound("speech.mp3")

def listen_for_keypress():
    global break_sleep
    while True:
        event = keyboard.read_event()  # Waits for any key event (press or release)
        # print(f"Event: {event}")
        if keyboard.is_pressed('esc'):
        # if event.event_type == "down":  # Triggers only on key press (not release)
            print('Break Sleep')
            break_sleep = True
            break


def main():

    global break_sleep
    # Step 1: Authenticate and get the Spotipy client
    sp = authenticate_spotify()

    # Pick a decade for your music playlist

    # View the list of songs by genre in your chosen decade
    # and choose the genre you want to listen to

    # Format of CLI
    # sys.argv[1] = filename  eg. 1960s
    # sys.argv[2] = genre   eg. folk
    # sys.argv[3] = mode    eg. top, bottom, random
    # sys.argv[4] = start_index  eg. 1-25


    file_name = '1960s.json'
    genre = "folk"
    mode = "forward"
    start_index = 0

    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    if len(sys.argv) > 2:
        genre = sys.argv[2]

    decade = file_name[:5]

    print(file_name, genre, mode, start_index)

    # Was getting error with ' char, needed to set this encoding
    with open(file_name, 'r', encoding="utf-8") as f:
        all_songs = json.load(f)


    songs = all_songs[genre]
    n = len(songs)

    if mode == "forward":
        for i in range(start_index, n):
            print(songs[i])

    elif mode == "backward":
        for i in range(start_index, -1, -1):
            print(songs[i])

    elif mode == "random":
        visited = set()  # To avoid duplicates
        while len(visited) < n:
            index = random.randint(0, n - 1)
            if index not in visited:
                visited.add(index)
                print(songs[index])

    input('Press Enter to Continue . . .')

    for song in all_songs[genre]:
        artist_name = song["artist"]
        track_name = song["song_name"]

        duration_ms = 0
        track_id, duration_ms = search_track(sp, artist_name, track_name)
        total_seconds = duration_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        print(f'Duration_ms = {duration_ms}')

        # Clear the screen
        # os.system('cls' if os.name == 'nt' else 'clear')
        # print("\033[H\033[J")
        print()
        print(f"   Rank # {song['rank']}  Genre: {genre}  Decade: {decade}   Released: {song['year']}")
        print()
        print(f"   Artist: {artist_name}    Song: {track_name}, Duration: {minutes}:{seconds:02}")
        print_track_description(all_songs, genre, song["rank"]-1)

        # Wait for the description to finish playing
        description_wait_time = 2
        time.sleep(description_wait_time)
        my_device_id = play_track(sp, track_id)

        # Flag to control the loop
        break_sleep = False

        # Start a thread to listen for key press
        listener_thread = threading.Thread(target=listen_for_keypress)
        listener_thread.daemon = True
        listener_thread.start()

        # Simulate a long-running task
        run_seconds = int(duration_ms/1000)
        print(f"Starting sleep, press any key to interrupt, seconds = {run_seconds}")

        for _ in range(run_seconds):  # Sleep in chunks of 1 second
            if break_sleep:
                print("Sleep interrupted")
                break
            time.sleep(1)
        else:
            print("Completed sleep without interruption")

        # This will stop the playback if interrupted by key press
        if break_sleep:
            sp.pause_playback(device_id=my_device_id)
            break_sleep = False

if __name__ == "__main__":
    main()

