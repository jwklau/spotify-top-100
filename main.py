from bs4 import BeautifulSoup
import requests
import pprint
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv("/Users/jenniferlau/Python/EnvironmentVariables/.env")

BILLBOARD_URL = "https://www.billboard.com/charts/hot-100"

SPOTIFY_CLIENT_ID = os.getenv("SpotifyClientID")
SPOTIFY_CLIENT_SECRET = os.getenv("SpotifyClientSecret")

OAUTH_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

time_travel_date = input("Which year do you want to travel to? Type it in this format: YYYY-MM-DD: ")
time_travel_year = time_travel_date.split("-")[0]

# Scraping Billboard website for top 100 songs in given year and month
response = requests.get(f"{BILLBOARD_URL}/{time_travel_date}")
billboard_webpage = response.text

soup = BeautifulSoup(billboard_webpage, "html.parser")
songs = soup.find_all(name="span", class_="chart-element__information__song text--truncate color--primary")
song_titles = [song.getText() for song in songs]

# Spotify authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri="https://example.com",
        scope="playlist-modify-private",
        show_dialog=True,
        cache_path="token.txt"
        )
    )

user_id = sp.current_user()["id"]

# Getting song URIs from top 100 song list
spotify_song_uris = []
for song in song_titles:
    try:
        result = sp.search(f"track: {song} year: {time_travel_year}")
        track_uri = result["tracks"]["items"][0]["uri"]
        spotify_song_uris.append(track_uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# Creating new private playlist
new_playlist = sp.user_playlist_create(user=user_id, name=f"{time_travel_date} Billboard 100", public=False)
playlist_id = new_playlist["id"]

# Adding tracks onto playlist
sp.playlist_add_items(playlist_id, spotify_song_uris)