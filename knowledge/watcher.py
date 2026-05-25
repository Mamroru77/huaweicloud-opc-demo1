import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from knowledge.manager import KnowledgeManager
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


class KnowledgeFileHandler(FileSystemEventHandler):
    def __init__(self, manager: KnowledgeManager):
        self.manager = manager

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent) and not event.is_directory:
            logger.info(f"知识库文件已修改: {event.src_path}")
            self.manager.clear_cache()


class FileWatcher:
    def __init__(self, watch_path: str, manager: KnowledgeManager):
        self.watch_path = watch_path
        self.manager = manager
        self.observer = Observer()
        self.handler = KnowledgeFileHandler(manager)

    def start(self):
        if not os.path.exists(self.watch_path):
            logger.warning(f"监听目录不存在: {self.watch_path}")
            return
        self.observer.schedule(self.handler, self.watch_path, recursive=True)
        self.observer.start()
        logger.info(f"开始监听知识库目录: {self.watch_path}")

    def stop(self):
        self.observer.stop()
        self.observer.join()
