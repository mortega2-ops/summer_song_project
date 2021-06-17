from django.shortcuts import render
from django.http import HttpResponse
from datetime import date
from bs4 import BeautifulSoup
import requests

# Create your views here.


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




