from django.shortcuts import render
from django.http import HttpResponse
from datetime import date
from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import json


def home(request):
    holiday_list = []
    holiday_key_words = []
    remove_words_list = ['Global', 'International', 'National', 'Day', 'Republic', 'Audacity to', 'of',
                         'Stand for', 'Wear a', 'I Love My', 'Awareness', 'Holiday', 'of the', 'World', 'First']

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

        holiday_regex = re.compile('|'.join(map(re.escape, remove_words_list)))
        for holiday in holiday_list:
            edited_holiday = holiday_regex.sub('', holiday)
            edited_holiday = edited_holiday.strip()
            holiday_key_words.append(edited_holiday)

        request.session['today'] = str(today_dict['today'])
        request.session['song_topics'] = holiday_key_words

        return render(request, "summer_song_app/home.html", today_dict)

    except Exception as e:
        print('The scraping job failed. See exception: ' + str(e))
        return HttpResponse('The scraping job failed. See exception: ' + str(e))


def playlist_gen(request):
    playlist = []
    recommended_song_list = []

    spotify = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(client_id='a25f7890ec934e0c9f9fb86b7bc00cd7',
                                                            client_secret='d9b515dbfa074cd9a358db90609c0567'))

    for key_word in request.session['song_topics']:
        playlist.append(spotify.search(q=key_word, limit=1, type='track', market=None))
        print(json.dumps(playlist, indent=4))
        # try:
        #     track_id = [results['tracks']['items'][0]['id']]
        #     playlist.append(spotify.recommendations(seed_tracks=track_id, limit=3))
        # except IndexError:
        #     print(f"{key_word} doesn't exist in Spotify.  Skipped.")

    for i in range(len(playlist)):
        for song in playlist[i]['tracks']['items']:
            print(song['name'])
            print(song['external_urls']['spotify'])
            recommended_song_list.append([song['name'], song['external_urls']['spotify']])

    song_dict = {
        'playlist': recommended_song_list
    }

    return render(request, 'summer_song_app/playlist.html', song_dict)
