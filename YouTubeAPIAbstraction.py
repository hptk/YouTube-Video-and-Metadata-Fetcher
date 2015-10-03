#!/usr/bin/env python3.5

from pprint import pprint
from urllib.request import urlopen
import json

_MAXRESULTS = 100
_TESTVID = "JjDsP5n2kSM"

class APIRequestStringBuilder:
    def __init__(self, url, resource, key):
        self.root = url + '/' + resource + '?'
        self.properties = {'key': [key]}

    def add(self, property_name, *property_values):
        try:
            self.properties[property_name] += property_values
        except KeyError:
            self.properties[property_name] = property_values

    def build(self):
        retval = self.root + '&'.join(map(lambda name: name + '=' + ','.join(self.properties[name]), self.properties.keys()))
        print(retval)
        return retval

class YouTubeAPI:
    def __init__(self, api_url, api_key):
        self.url = api_url
        self.key = api_key

    def getComments(self, video_id, results=[], page_token='', depth=1, get_replies=False):
        request = APIRequestStringBuilder(self.url, 'commentThreads', self.key)
        request.add('part', 'snippet')
        request.add('maxResults', str(_MAXRESULTS))
        request.add('videoId', video_id)
        if page_token != '':
            request.add('pageToken', page_token)
        if get_replies:
            request.add('part', 'replies')

        result = json.loads(urlopen(request.build()).read().decode())

        if not result['items']:
            return results

        results += result['items']

        if result['pageInfo']['totalResults'] == result['pageInfo']['resultsPerPage']:
            print('YouTubeAPI.getComments(' + depth + '): got ' + result['pageInfo']['totalResults'] + ' results!')
            return getComments(video_id, results, result['pageNextToken'], depth+1)

        return results



if __name__ == "__main__":
    with open('dash_wallenburg_youtube_apikey_1') as apikeyfile:
        test = YouTubeAPI('https://www.googleapis.com/youtube/v3',
                          apikeyfile.readline().rstrip())

    pprint(test.getComments(_TESTVID))
    #print(test.getComments('h1Uxlnv12NY'))
