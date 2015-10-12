from flask import Flask, render_template, request
from RenameMe import getCommentsHandler

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
def getComments():
    return getCommentsHandler(request.args)

if __name__ == '__main__':
    app.run(debug=True)
