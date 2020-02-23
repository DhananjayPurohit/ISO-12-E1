from pytrends.request import TrendReq
from youtube_search import YoutubeSearch as ys
import wikipediaapi

keyword = ['java']

class Trends():
    def __init__(self, keyword):
        self.keyword = keyword
        self.pyt = TrendReq(hl='en-US', tz=360,timeout=(10,25), retries=2, backoff_factor=0.1)
        self.web = self.pyt.get_historical_interest(self.keyword, year_start=2018,
                            month_start=1, day_start=1, hour_start=0, cat=0,
                            geo='', gprop='', sleep=0)
        self.you = self.pyt.get_historical_interest(self.keyword, year_start=2018,
                            month_start=1, day_start=1, hour_start=0, cat=0,
                            geo='', gprop='youtube', sleep=0)
        self.pref()

    def pref(self):
        if self.web.mean()[self.keyword[0]] > self.you.mean()[self.keyword[0]]:
            self.preference_video = False
        else:
            self.preference_video = True

        return self.preference_video

    def get_content(self):
        if self.preference_video:
            print("Youtube Video")
            self.youtube_link = ys(self.keyword[0], max_results=5).to_json()
            self.link = eval(self.youtube_link)['videos'][0]['link']
            return "http://youtube.com"+self.link
        else:
            print("Text Content")
            self.wiki = wikipediaapi.Wikipedia('en')
            if self.wiki.page(self.keyword[0]).exists():
                self.summary = self.wiki.page(self.keyword[0]).summary
            else:
                self.summary = "No info found !"
            return self.summary

class getCONTENT():
    def __init__(self, preference, keyword):
        self.keyword = keyword
        self.preference_video = preference
        if self.preference_video:
            print("Youtube Video")
            self.youtube_link = ys(self.keyword[0], max_results=5).to_json()
            self.link = eval(self.youtube_link)['videos'][0]['link']
            self.summary= "http://youtube.com"+self.link
        else:
            print("Text Content")
            self.wiki = wikipediaapi.Wikipedia('en')
            if self.wiki.page(self.keyword[0]).exists():
                self.summary = self.wiki.page(self.keyword[0]).summary
            else:
                self.summary = "No info found !"
