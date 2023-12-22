import json
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from helpers import init_db
from models import db
from models import Score


app = Flask(__name__, static_url_path='/static')

DB_NAME = 'interstellar-inferno.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

init_db(app, db, DB_NAME)
db.init_app(app)

# Assuming the zip file is located at /static/files/INTERSTELLAR_INFERNO.zip
# ZIP_FILE_PATH = '/static/files/InterstellarInferno.zip'
DOWNLOAD_FOLDER = 'static/files'  # This should be the folder where your zip file is located
DOWNLOAD_FILENAME = 'InterstellarInferno.zip'

# Website routes
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/games')
def games():
    return render_template('games.html')
@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/games/interstellar-inferno')
def interstellar_inferno_index():
    return render_template('insterstellar-inferno/index.html')

@app.route('/games/interstellar-inferno/download')
def interstellar_inferno_download_file():
    try:
        return send_from_directory(DOWNLOAD_FOLDER, DOWNLOAD_FILENAME, as_attachment=True)
    except:
        print('file not found')
        return "Could not find file to download"


@app.route('/games/interstellar-inferno/wiki')
def interstellar_inferno_wiki():
    return render_template('insterstellar-inferno/wiki.html')

@app.route('/games/interstellar-inferno/news')
def interstellar_inferno_news():
    return render_template('insterstellar-inferno/news.html')

@app.route('/games/interstellar-inferno/leaderboard')
def interstellar_inferno_leaderboard():
    scores = Score.query.all()
    return render_template('insterstellar-inferno/leaderboard.html', scores=scores)




# API ROUTES
@app.route('/api/interstellar-inferno/submit_score',methods=['POST'])
def submit_score():
    if request.method == 'POST':
        data = request.get_json()
        newscore = Score(username=data.get('username'), score=data.get('score'))
        db.session.add(newscore)
        db.session.commit()
        return jsonify(newscore.as_dict())
    
@app.route('/api/interstellar-inferno/leaderboard')
def leaderboard_api():
    scores = Score.query.all()
    return jsonify([score.as_dict() for score in scores])   

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=7373,debug=True)