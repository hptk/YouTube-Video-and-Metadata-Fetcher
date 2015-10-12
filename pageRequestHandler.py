from YouTubeAPIAbstraction import YouTubeAPI

baseURL = "https://www.googleapis.com/youtube/v3"

def getCommentsHandler(args):
    APIkey = args.get('key')
    temp = YouTubeAPI(baseURL, APIkey)

    try:
        videoID = args.get('videoID')
        res = temp.getComments(videoID)
        return str(res)
    except KeyError:
        return "Error"
