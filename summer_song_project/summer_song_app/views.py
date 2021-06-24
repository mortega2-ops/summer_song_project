from pprint import pprint
from django.http import HttpResponse
from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import date
import re
import json

SPOTIPY_CLIENT_ID = 'need this'
SPOTIPY_CLIENT_SECRET = 'need this'


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

        request.session['today'] = str(today_dict['today'])
        holiday_key_words = []
        remove_words_list = ['Global', 'International', 'National', 'Day', 'Republic', 'Audacity to', 'of', 'Stand for',
                             'Wear a', 'I Love My', 'Awareness', 'Holiday', 'of the', 'World', 'First']
        holiday_regex = re.compile('|'.join(map(re.escape, remove_words_list)))

        for holiday in holiday_list:
            edited_holiday = holiday_regex.sub('', holiday)
            edited_holiday = edited_holiday.strip()
            holiday_key_words.append(edited_holiday)

        request.session['song_topics'] = holiday_key_words
        return render(request, "summer_song_app/home.html", today_dict)

    except Exception as e:
        print('The scraping job failed.  See exception: ' + str(e))
        return HttpResponse('The scraping job failed.  See exception: ' + str(e))


def getsongs(request):
    this_day = request.session['today']

    try:
        # desired_date = request.GET.get('end_date', '2021-06-15')
        my_year = request.GET.get('desired_year', '2021')

        if not my_year:
            my_year = '2021'
        desired_date = (my_year + this_day[4:])
        response = requests.get("https://www.billboard.com/charts/hot-100/" + desired_date)

        soup = BeautifulSoup(response.text, 'html.parser')
        song_names_spans = soup.find_all("span", class_="chart-element__information__song")
        song_names = [song.getText() for song in song_names_spans]

    except Exception:
        print("Error attempting to get song list from billboard.com")

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri="https://example.com",
            scope="playlist-modify-private",
            show_dialog=True,
            cache_path="../../token.txt"
            # cache_path="token.txt"
        ))

    user_id = sp.current_user()["id"]

    song_uris = []
    year = desired_date.split("-")[0]
    for song in song_names:
        result = sp.search(q=song, type="track")
        # result = sp.search(q=f"track: {song} year: {year}", type="track")
        try:
            uri = result["tracks"]["items"][0]["uri"]
            song_uris.append(uri)
        except IndexError:
            print(f"{song} doesn't exist in Spotify.  Skipped.")

    playlist = sp.user_playlist_create(user=user_id, name=f"{desired_date} Billboard 100", public=False)

    playlist_urls = playlist["external_urls"]
    my_playlist_url = playlist_urls["spotify"]

    sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

    spot = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri="https://example.com",
            scope="playlist-modify-private",
            show_dialog=True,
            cache_path="../../token.txt"
            # cache_path="token.txt"
        ))

    user_id = spot.current_user()["id"]

    this_days_songs = request.session['song_topics']
    topic_uris = []
    for topic in this_days_songs:
        results = spot.search(q=topic, limit=4, type='track', market=None)
        with open('display_results.txt', mode="w") as search_results:
            search_results.write(json.dumps(results, sort_keys=True, indent=4))
        try:
            for i in results["tracks"]["items"]:
                # topic_uri = results["tracks"]["items"][i]["uri"]
                topic_uri = i["uri"]
                topic_uris.append(topic_uri)
        except IndexError:
            print(f"{topic} doesn't exist in Spotify.  Skipped.")

    topic_playlist = spot.user_playlist_create(user=user_id, name=f"Today's Holiday Playlist", public=False)
    topic_playlist_urls = topic_playlist["external_urls"]
    my_topic_playlist_url = topic_playlist_urls["spotify"]
    spot.playlist_add_items(playlist_id=topic_playlist["id"], items=topic_uris)

    return render(request, "summer_song_app/getsongs.html", {"playlist": my_playlist_url, "desired_date": desired_date,
                                                             "holiday_playlist": my_topic_playlist_url,
                                                             "today": this_day})
