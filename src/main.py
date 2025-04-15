# Import and apply eventlet monkey patch before any other imports
import eventlet
eventlet.monkey_patch()

import json
import logging
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from helpers import init_db
from models import Article, db
from models import Score

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_url_path='/static')

DB_NAME = 'interstellar-inferno.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['SECRET_KEY'] = 'secret-key-for-socketio'  # Required for SocketIO

# Initialize SocketIO with simpler configuration
socketio = SocketIO(app, 
                   cors_allowed_origins="*", 
                   logger=True,
                   engineio_logger=True)

db.init_app(app)
with app.app_context():
    db.create_all()

# Assuming the zip file is located at /static/files/INTERSTELLAR_INFERNO.zip
# ZIP_FILE_PATH = '/static/files/InterstellarInferno.zip'
DOWNLOAD_FOLDER = 'static/files'  # This should be the folder where your zip file is located
DOWNLOAD_FILENAME = 'InterstellarInferno1.zip'

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
@app.route('/faq')
def faq():
    return render_template('faq.html')



@app.route('/games/interstellar-inferno')
def interstellar_inferno_index():
    return render_template('insterstellar-inferno/index.html')

@app.route('/games/interstellar-inferno/download')
def interstellar_inferno_download_file():
    try:
        return send_from_directory(DOWNLOAD_FOLDER, DOWNLOAD_FILENAME, as_attachment=True)
    except:
        print('file not found')
        return "The game is not "


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

# Add a diagnostic route for WebSocket testing
@app.route('/socket-test')
def socket_test():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test</title>
        <script src="https://cdn.socket.io/4.4.1/socket.io.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', () => {
                const statusDiv = document.getElementById('status');
                const logDiv = document.getElementById('log');
                
                function log(msg) {
                    const p = document.createElement('p');
                    p.textContent = msg;
                    logDiv.appendChild(p);
                    console.log(msg);
                }
                
                statusDiv.textContent = "Connecting...";
                
                // Simple connection with default options
                const socket = io();
                
                socket.on('connect', () => {
                    statusDiv.textContent = "Connected!";
                    statusDiv.className = "connected";
                    log(`Connected with transport: ${socket.io.engine.transport.name}`);
                    
                    // Request a ping to test bidirectional communication
                    socket.emit('ping_test');
                });
                
                socket.on('disconnect', () => {
                    statusDiv.textContent = "Disconnected";
                    statusDiv.className = "disconnected";
                    log("Disconnected from server");
                });
                
                socket.on('connect_error', (err) => {
                    statusDiv.textContent = `Connection Error: ${err.message}`;
                    statusDiv.className = "error";
                    log(`Connection error: ${err.message}`);
                });
                
                socket.on('pong_test', () => {
                    log("Received pong from server!");
                });
            });
        </script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #status { padding: 10px; margin-bottom: 10px; border-radius: 5px; font-weight: bold; }
            .connected { background-color: #dff0d8; color: #3c763d; }
            .disconnected { background-color: #f2dede; color: #a94442; }
            .error { background-color: #fcf8e3; color: #8a6d3b; }
            #log { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <h1>WebSocket Test Page</h1>
        <div id="status">Initializing...</div>
        <h3>Connection Log:</h3>
        <div id="log"></div>
    </body>
    </html>
    """

# API ROUTES
@app.route('/api/interstellar-inferno/submit_score',methods=['POST'])
def submit_score():
    if request.method == 'POST':
        data = request.get_json()
        newscore = Score(username=data.get('username'), score=data.get('score'),planets=data.get('planets'))
        db.session.add(newscore)
        db.session.commit()
        
        # Emit the new score to all connected clients
        socketio.emit('new_score', newscore.as_dict())
        
        return jsonify(newscore.as_dict())
    
@app.route('/api/interstellar-inferno/leaderboard')
def leaderboard_api():
    scores = Score.query.all()
    return jsonify([score.as_dict() for score in scores])


@app.route('/api/news/publish', methods=['POST'])
def publish_news():
    if request.method == 'POST':
        data = request.get_json()
        newarticle = Article(title=data.get('title'), subtitle=data.get('subtitle'),type=data.get('type'))
        db.session.add(newarticle)
        db.session.commit()
        return jsonify(newarticle.as_dict())

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    # Send the current leaderboard to the newly connected client
    scores = Score.query.order_by(Score.score.desc()).all()
    emit('init_leaderboard', [score.as_dict() for score in scores])

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('ping_test')
def handle_ping():
    logger.info('Received ping test, sending pong')
    emit('pong_test')

if __name__ == '__main__':
    # Run with eventlet web server
    logger.info("Starting Flask-SocketIO server...")
    socketio.run(app, 
                host="0.0.0.0", 
                port=80, 
                debug=False, 
                use_reloader=False)  # Disable reloader for better stability in Docker
