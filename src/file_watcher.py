import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import update_configmap

class VideosJsonHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('videos.json'):
            print("Detected change in videos.json, updating ConfigMap...")
            update_configmap.update_videos_configmap()

if __name__ == "__main__":
    path = "."  # Directory to watch
    event_handler = VideosJsonHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()