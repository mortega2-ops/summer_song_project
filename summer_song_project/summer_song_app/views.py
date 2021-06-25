from django.shortcuts import render
from django.http import HttpResponse
from datetime import date
from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json


def home(request):
    holiday_list = []

    try:
        r = requests.get('https://nationaltoday.com/what-is-today/')
        soup = BeautifulSoup(r.content, "lxml")
        what_is_today = soup.find("h2", class_="entry-title").text
        other_holidays_today = soup.find_all("p", class_="holiday-title")

        holiday_list.append(what_is_today)
        for day in other_holidays_today:
            holiday_list.append(day.text)

        today_dict = {
            'todays_holidays': holiday_list,
            'today': date.today()
        }

        return render(request, "summer_song_app/home.html", today_dict)

    except Exception as e:
        print('The scraping job failed. See exception: ' + str(e))
        return HttpResponse('The scraping job failed. See exception: ' + str(e))


def playlist_gen(request):
    recommended_song_list = []

    spotify = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(client_id='a25f7890ec934e0c9f9fb86b7bc00cd7',
                                                            client_secret='d9b515dbfa074cd9a358db90609c0567'))

    results = spotify.search(q='Eat+Your+Vegetables', limit=1, type='track', market=None)
    # print(json.dumps(results, sort_keys=True, indent=4))
    # print(type(results))
    # print(json.dumps(results['tracks']['items'][0]['id'], sort_keys=True, indent=2))

    track_id = [results['tracks']['items'][0]['id']]
    playlist = spotify.recommendations(seed_tracks=track_id, limit=10)

    for song in playlist['tracks']:
        print(song['name'])
        print(song['external_urls']['spotify'])
        recommended_song_list.append([song['name'], song['external_urls']['spotify']])

    song_dict = {
        'spotify_url': results['tracks']['items'][0]['external_urls']['spotify'],
        'song_name': results['tracks']['items'][0]['name'],
        'playlist': recommended_song_list
    }

    # print(json.dumps(playlist, sort_keys=True, indent=4))
    # print(playlist['tracks'][0]['name'])





    return render(request, 'summer_song_app/playlist.html', song_dict)




