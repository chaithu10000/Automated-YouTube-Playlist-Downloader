import os
from flask import Flask, render_template_string, request
from googleapiclient.discovery import build
import yt_dlp as ytdlp

# Initialize Flask app
app = Flask(__name__)

# Set the download path
DOWNLOAD_PATH = "downloads"

# Ensure the download directory exists
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

API_KEY = 'AIzaSyAp7vnV2FEOCHmLgjPhzodMd0u2ASE2pZc'

def download_playlist_videos(playlist_id):
    """Function to download videos from a YouTube playlist using yt-dlp."""
    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
        'format': 'best',
        'noplaylist': False,  # Download the entire playlist
    }
    
    try:
        with ytdlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(playlist_url, download=True)
            video_count = len(info_dict.get('entries', []))
            return f"Downloaded {video_count} videos to {DOWNLOAD_PATH}"
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while downloading the playlist."

def get_top_playlists(query, max_results=5):
    """Function to search for top YouTube playlists based on the query."""
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='playlist',
        maxResults=max_results
    )
    response = request.execute()

    playlists = []
    for item in response['items']:
        playlists.append({
            'title': item['snippet']['title'],
            'channel': item['snippet']['channelTitle'],
            'playlistId': item['id']['playlistId']
        })

    return playlists

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Playlist Downloader</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f9f9f9;
            margin: 0;
            padding: 0;
            color: #333;
        }
        .container {
            width: 80%;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background-color: #282c34;
            color: #ffffff;
            padding: 20px;
            text-align: center;
            border-bottom: 4px solid #61dafb;
        }
        h1 {
            margin: 0;
        }
        form {
            background: #ffffff;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        label {
            font-size: 1.2em;
            margin-bottom: 10px;
            display: block;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            font-size: 1em;
            border: 2px solid #ccc;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        button {
            background-color: #61dafb;
            border: none;
            color: #ffffff;
            padding: 10px 20px;
            font-size: 1.1em;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        button:hover {
            background-color: #21a1f1;
        }
        .playlist-item {
            background: #ffffff;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .playlist-item input[type="radio"] {
            margin-right: 10px;
        }
        .status {
            background: #ffffff;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .status p {
            margin: 0;
        }
    </style>
</head>
<body>
    <header>
        <h1>YouTube Playlist Downloader</h1>
    </header>
    <div class="container">
        <form method="POST" action="/search">
            <label for="query">Enter a topic:</label>
            <input type="text" id="query" name="query" required>
            <button type="submit">Search</button>
        </form>
        {% if playlists %}
            <h2>Top Playlists for "{{ query }}"</h2>
            <form method="POST" action="/download">
                {% for playlist in playlists %}
                    <div class="playlist-item">
                        <input type="radio" id="{{ playlist.playlistId }}" name="playlistId" value="{{ playlist.playlistId }}" required>
                        <label for="{{ playlist.playlistId }}">{{ playlist.title }} by {{ playlist.channel }}</label>
                    </div>
                {% endfor %}
                <button type="submit">Download Selected Playlist</button>
            </form>
        {% endif %}
        {% if message %}
            <div class="status">
                <p>{{ message }}</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    playlists = get_top_playlists(query)
    return render_template_string(HTML_TEMPLATE, playlists=playlists, query=query)

@app.route('/download', methods=['POST'])
def download():
    playlist_id = request.form['playlistId']
    download_message = download_playlist_videos(playlist_id)
    return render_template_string(HTML_TEMPLATE, message=download_message)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
