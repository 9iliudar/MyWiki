import time
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class InboxHandler(FileSystemEventHandler):
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def on_created(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith(".md"):
            return

        time.sleep(1)
        path = Path(event.src_path)
        if not path.exists():
            return

        print(f"检测到新素材: {path.name}")
        try:
            result = self.pipeline.ingest_file(str(path))
            print(f"  已消化: {result['summary'][:60]}")
            print(f"  影响页面: {', '.join(result['pages_affected'])}")
        except Exception as e:
            print(f"  消化失败: {e}")


def start_watching(inbox_dir: str, pipeline):
    handler = InboxHandler(pipeline)
    observer = Observer()
    observer.schedule(handler, inbox_dir, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
