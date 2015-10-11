from flask import Flask, render_template
from YouTubeAPIAbstraction import YouTubeAPI
app = Flask(__name__)

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

@app.route('/')
def index():
    return render_template('index.jjhtml')

@app.route('/hello/<name>/')
def hello(name=None):
    return render_template('hello.jjhtml', name=name)

@app.route('/getComments/')
@app.route('/getComments/<videoID>/')
def getComments(videoID='9bZkp7q19f0'):
    with open('APIkey') as apikeyfile:
        temp = YouTubeAPI('https://www.googleapis.com/youtube/v3', apikeyfile.readline().rstrip())
    res = temp.getComments(videoID)
    return str(res)

if __name__ == '__main__':
    app.run(debug=True)
