
from urllib2 import urlopen, unquote;
from urlparse import parse_qs;
import xmltodict
import json
video_id = "nT6eaBm82bQ"

def get_video_info(video_id):
    return parse_qs(unquote(urlopen('http://www.youtube.com/get_video_info?&video_id=' + video_id).read().decode('utf-8')))

def get_video_manifest(url):
    return urlopen(url).read()

def manifest_to_dict(manifest):
    return json.dumps(xmltodict.parse(manifest), indent=4, separators=(',', ': '))

video_info = get_video_info(video_id)

manifest = get_video_manifest(video_info["dashmpd"][0])
print(manifest_to_dict(manifest))
