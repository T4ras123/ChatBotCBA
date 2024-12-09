from flask import Flask, render_template, request, redirect, url_for
import json
import os



app = Flask(__name__)

VIDEOS_FILE = 'videos.json'

def load_videos():
    if not os.path.exists(VIDEOS_FILE):
        # Initialize videos.json with an empty list
        with open(VIDEOS_FILE, 'w') as f:
            json.dump([], f)
        return []
    with open(VIDEOS_FILE, 'r') as f:
        return json.load(f)
    
def save_videos(videos):
    with open(VIDEOS_FILE, 'w') as f:
        json.dump(videos, f, indent=4)

@app.route('/')
def index():
    videos = load_videos()
    return render_template('index.html', videos=videos)

@app.route('/add', methods=['GET', 'POST'])
def add_video():
    if request.method == 'POST':
        new_video = {
            'title': request.form['title'],
            'text': request.form['text'],
            'link': request.form['link']
        }
        videos = load_videos()
        videos.append(new_video)
        save_videos(videos)
        return redirect(url_for('index'))
    return render_template('add_video.html')
  
def save_videos(videos):
    with open(VIDEOS_FILE, 'w') as f:
        json.dump(videos, f, indent=4)
    # Update the ConfigMap after saving

# Additional routes for edit and delete can be added similarly

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)