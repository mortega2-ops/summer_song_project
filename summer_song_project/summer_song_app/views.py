from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth


SPOTIPY_CLIENT_ID = ''
SPOTIPY_CLIENT_SECRET = ''


# Create your views here.


def home(request):
    return render(request, "summer_song_app/home.html")


# def get_name(request):
#     # if this is a POST request we need to process the form data
#     if request.method == 'POST':
#         # create a form instance and populate it with data from the request:
#         form = NameForm(request.POST)
#         # check whether it's valid:
#         if form.is_valid():
#             # process the data in form.cleaned_data as required
#             # ...
#             # redirect to a new URL:
#             return HttpResponseRedirect('/thanks/')
#
#     # if a GET (or any other method) we'll create a blank form
#     else:
#         form = NameForm()
#
#     return render(request, 'name.html', {'form': form})


def getsongs(request):
    # end_date = input('What date would you like to go to? (Birthdate? '
    #                  'Type the date in this format:  YYYY-MM-DD: ')

    # def get(self, request):
    #     form = GetYearForm()
    #     return render(request, )

    desired_date = request.GET.get('end_date', '2021-06-15')
    response = requests.get("https://www.billboard.com/charts/hot-100/" + desired_date)

    soup = BeautifulSoup(response.text, 'html.parser')
    song_names_spans = soup.find_all("span", class_="chart-element__information__song text--truncate color--primary")
    song_names = [song.getText() for song in song_names_spans]

    print(soup.prettify())
    print(song_names)

    scope = "user-library-read"
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri="https://example.com",
            scope="playlist-modify-private",
            show_dialog=True,
            cache_path="token.txt"
        ))

    user_id = sp.current_user()["id"]

    song_uris = []
    year = desired_date.split("-")[0]
    for song in song_names:
        result = sp.search(q=f"track: {song} year: {year}", type="track")

    # return render(request, "summer_song_app/getsongs.html", {'desired_date': chosen_date})
