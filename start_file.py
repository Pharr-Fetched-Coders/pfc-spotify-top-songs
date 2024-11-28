# 01:11 11/4/24
import webbrowser
import json
from dotenv import load_dotenv
import os
import sys
import base64
import pprint as pp
from requests import post, get, put
import textwrap
from rich import print
from rich.console import Console
from gtts import gTTS


load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
user_id = os.getenv("SPOTIFY_USER_ID")
print(f"My Spotify User ID = {user_id}")


def main():

    # Get Spotify Token
    token = get_token()
    print(f'Spotify Token = {token}\n')

    # initial_setup()
    file_name = '1960s.json'
    decade = file_name[:5]
    # Was getting error with ' char, needed to set this encoding
    with open(file_name, 'r', encoding="utf-8") as f:
        all_songs = json.load(f)

    # This will print the entire json file
    # pp.pprint(all_songs)

    # show_songs(all_songs, decade)

    country_songs = []
    for song in all_songs["soft_rock"]:
        print(f"{song['rank']:>5}   {song['year']:<2}   {song['artist']:<30}. . . . {song['song_name']:<40}")
        # pp.pprint(f"{song['description']}")
        # print()
        # country_songs.append(song["song_name"])

    # Set genre and song index to 1st song for testing
    genre = 'soft_rock'
    song_index = 0
    # Get the song name and artist from
    song_name = all_songs[genre][song_index]["song_name"]
    song_artist = all_songs[genre][song_index]["artist"]

    # Print out the top header
    console = Console(width=60)
    console.rule("[bold red]Description Start")
    print()

    # Print out the track description
    wrapped_text = textwrap.fill(all_songs[genre][song_index]['description'], width=50)
    console.print(wrapped_text, justify="center")
    print()

    # Print out the bottom header
    console.rule("[bold red]Description End")
    print()

    # Create a speech file of description
    tts = gTTS(all_songs[genre][song_index]['description'])
    tts.save("speech.mp3")

    # print(f"Artist Name: {song_artist}       Song Name: {song_name} ")

    # This returns the json results for search
    tracks = search_for_song(token, song_artist, song_name)
    # pp.pprint(tracks)

    for idx, track in enumerate(tracks):
        print(f'{idx + 1}. {track["name"]}')
        pp.pprint(track['artists'])
        print()
        pp.pprint(track['name'])
        print()
        # Get the 1st artist name
        artist = tracks[idx]["album"]["artists"][0]["name"][:19]
        # Get the 1st artist's track ID
        artist_id = tracks[idx]["album"]["artists"][0]["id"][:19]
        print(f'Artist Name = {artist:<50} {"Artist ID":<5} =  {artist_id}')

        track_name = track['name']
        track_id = track['id']
        print(f'Track Name = {track_name:<50}  Track ID = {track_id}')
        play_track(token, track_id)

        # webbrowser.open(f"https://open.spotify.com/track/{track_id}")


# This is still work in progress
# This will allow the user to select a genre and then select a song to play
def show_songs(all_songs, decade):
    # Print all the Genre names in the file
    genre_keys = list(all_songs.keys())
    print(f"\nGenres in this file are: {genre_keys}\n")
    print(f'Welcome to the Songs of the {decade}')
    print(f"The Genre Keys are:    {' , '.join(genre_keys)}\n")

    while True:
        print(f'\nChoose an Option: ')
        print(f'1: List Songs by Genre')
        print(f'2: List of Artists in Alphabetical Order')
        print(f'3: List of Song Titles in Alphabetical Order')
        choice = input('Enter Selection: ')
        if choice == '1':
            chosen_songs = songs_by_genre(all_songs)
        elif choice == '2':
            chosen_songs = songs_by_artist(all_songs)
        elif choice == 3:
            chosen_songs = songs_by_title(all_songs)
        else:
            print('\nExiting Program!\n')
            sys.exit()

def songs_by_genre(all_songs):
    while True:

        # Make list of Genres
        for i, genre in enumerate(all_songs.keys()):
            print(f'{i + 1}: {genre}')

        # User select Genre bu number
        choice = input("Enter Choice for Genre: ")

        # Make sure that input is valid
        if choice in ['1', '2', '3', '4']:
            chosen_genre = list(all_songs.keys())[int(choice) - 1]

            # List options for chosen genre
            print(f'\nChosen Genre is: {chosen_genre}\n')
            print('Option 1: View list of Songs')
            print('Option 2: Choose this Genre for Playing')

            # Get answer from user
            ans = input(f'Enter Selected Option :')

            # Option 1: View List of Songs for genre chosen
            if ans == '1':
                # pp.pprint(all_songs[chosen_genre])
                print(f'\n{"Rank":<7} {"Artist":<31} {"Year":<8}  {"Title":<40}')
                for song in all_songs[chosen_genre]:
                    print(f"{song['rank']:<6}  {song['artist']:<30}  {song['year']:<6}    {song['song_name']:<20}")
            elif ans == '2':
                pass
            else:
                sys.exit()
        else:

            sys.exit()

        # genre_keys = list(all_songs.keys())
        # print(f"The Genre Keys are:    {' , '.join(genre_keys)}\n")

        return []

def songs_by_artist(all_songs):
    return []

def songs_by_title(all_songs):
    return []

def initial_setup():
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    print(f'My Client ID = {client_id}')
    client_secret = os.getenv("CLIENT_SECRET")
    print(f'My Client Secret = {client_secret}')
    user_id = os.getenv("SPOTIFY_USER_ID")
    print("My Spotify User ID is : " + user_id)

# Not currently used, this code was put into main
def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    # pp.pp(result)
    json_result = json.loads(result.content)
    # pp.pprint(json_result)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_song(token, song_artist, song_name):
    url_base = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    # Get the 1st artist information
    query = f"?q=remaster%track%{song_name}%{song_artist}&type=track&limit=1"

    query_url = url_base + query
    # print(query_url)

    # Get result from Spotify
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["tracks"]["items"]
    # pp.pprint(json_result)

    return json_result

def play_track(token, track_id):

    # webbrowser.open("https://open.spotify.com/album/0ucV57dbnqmrGv9d60r6X2")

    '''
    headers = get_auth_header(token)
    print(f'Headers = {headers}')
    url_base = "https://api.spotify.com/v1/me/player/devices/"
    result = get(url_base, headers=headers)
    print(f'Result from 1st get {result}')
    devices = result.json()
    # print(devices)
    '''

    url_base = f"https://api.spotify.com/v1/me/player/play?device_id=0d1841b0976bae2a3a310dd74c0f3df354899bc8"

    # headers = get_auth_header(token)
    header1 = {'Authorization': 'Bearer' + token, 'Content-Type': 'application/json'}

    query = f"'uris': [spotify:track:{track_id}]"

    # query_url = url_base + query
    # print(query_url)
    # result = put(url_base, headers=headers, data={query_url})'
    # data = '{"context_uri": "spotify:album:5ht7ItJgpBH7W6vJ5BqpPr", "offset": {"position": 5},"position_ms": 0}'
    # data = '{"uris": "spotify:track:6YffUZJ2R06kyxyK6onezL"}'
    '''
        data = json.loads('{"uris": "spotify:track:6YffUZJ2R06kyxyK6onezL"}')
        print(url_base)
        pp.pprint(header1)
        print(data)
        result = put(url_base, headers=header1, data=data)
        # result = put(http://open.spotify.com/track/)
        print(result)
     '''


main()
