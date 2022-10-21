from flask import Flask
from flask_frozen import Freezer

app = Flask(__name__)

@app.route("/")
def wip():
    return """
<!DOCTYPE shameless-html>
<head><title>PyConFr 2023</title></head>
<body>
<h1>Work in progress</h1>
<shame state=absent>
    <marquee simulate=1990 direction=down behavior=alternate>
        <marquee class=yes direction=right behavior=alternate>
            <h2>👷👷👷</h2>
        </marquee>
    </marquee>
    <marquee class=club country=london direction=up style=rock behavior=alternate>
        <marquee direction=left behavior=alternate>
            <h2>👷👷👷</h2>
        </marquee>
    </marquee>
</shame>
</body>
"""


@app.cli.command('freeze')
def freeze():
    Freezer(app).freeze()
