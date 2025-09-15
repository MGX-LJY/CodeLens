"""
文件监控器 - 监控Python文件变化并触发重载
"""

import os
import time
from pathlib import Path
from typing import Set, List, Callable, Optional
from threading import Thread, Event
import asyncio
from concurrent.futures import ThreadPoolExecutor

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # 创建占位符类，防止NameError
    class FileSystemEventHandler:
        pass
    class FileModifiedEvent:
        pass
    class FileCreatedEvent:
        pass
    Observer = None
    print("⚠️  watchdog not available, falling back to polling mode")

from src.logging import get_logger

class FileChangeHandler(FileSystemEventHandler):
    """文件变化事件处理器"""
    
    def __init__(self, callback: Callable[[str], None], debounce_seconds: float = 0.5):
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.last_modified = {}
        self.logger = get_logger("FileWatcher", "file_change_detection")
    
    def on_modified(self, event):
        if isinstance(event, (FileModifiedEvent, FileCreatedEvent)) and event.src_path.endswith('.py'):
            self._handle_change(event.src_path)
    
    def on_created(self, event):
        if isinstance(event, FileCreatedEvent) and event.src_path.endswith('.py'):
            self._handle_change(event.src_path)
    
    def _handle_change(self, file_path: str):
        """处理文件变化，包含防抖动逻辑"""
        current_time = time.time()
        last_time = self.last_modified.get(file_path, 0)
        
        if current_time - last_time > self.debounce_seconds:
            self.last_modified[file_path] = current_time
            self.logger.info(f"检测到文件变化: {file_path}")
            self.callback(file_path)

class PollingWatcher:
    """轮询模式文件监控器（fallback方案）"""
    
    def __init__(self, paths: List[str], callback: Callable[[str], None], interval: float = 1.0):
        self.paths = [Path(p) for p in paths]
        self.callback = callback
        self.interval = interval
        self.file_mtimes = {}
        self.running = False
        self.thread: Optional[Thread] = None
        self.logger = get_logger("PollingWatcher", "file_polling")
    
    def start(self):
        """启动轮询监控"""
        if not self.running:
            self.running = True
            self.thread = Thread(target=self._poll_loop, daemon=True)
            self.thread.start()
            self.logger.info(f"启动轮询模式文件监控，间隔: {self.interval}s")
    
    def stop(self):
        """停止轮询监控"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _poll_loop(self):
        """轮询循环"""
        while self.running:
            try:
                self._check_files()
                time.sleep(self.interval)
            except Exception as e:
                self.logger.error(f"轮询检查文件时出错: {e}")
    
    def _check_files(self):
        """检查文件修改时间"""
        for path in self.paths:
            if path.is_dir():
                for py_file in path.rglob("*.py"):
                    self._check_file(py_file)
            elif path.is_file() and path.suffix == '.py':
                self._check_file(path)
    
    def _check_file(self, file_path: Path):
        """检查单个文件的修改时间"""
        try:
            mtime = file_path.stat().st_mtime
            if str(file_path) not in self.file_mtimes:
                self.file_mtimes[str(file_path)] = mtime
            elif mtime > self.file_mtimes[str(file_path)]:
                self.file_mtimes[str(file_path)] = mtime
                self.logger.info(f"检测到文件变化: {file_path}")
                self.callback(str(file_path))
        except OSError:
            # 文件可能被删除
            pass

class FileWatcher:
    """文件监控器主类"""
    
    def __init__(self, callback: Callable[[str], None], debounce_seconds: float = 0.5):
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.observer: Optional[Observer] = None
        self.polling_watcher: Optional[PollingWatcher] = None
        self.watched_paths: Set[str] = set()
        self.logger = get_logger("FileWatcher", "main")
        self.use_watchdog = WATCHDOG_AVAILABLE
        
        if not self.use_watchdog:
            self.logger.warning("watchdog库不可用，使用轮询模式监控文件")
    
    def add_path(self, path: str):
        """添加监控路径"""
        path = os.path.abspath(path)
        if path not in self.watched_paths:
            self.watched_paths.add(path)
            self.logger.info(f"添加监控路径: {path}")
    
    def start(self):
        """启动文件监控"""
        if not self.watched_paths:
            self.logger.warning("没有设置监控路径")
            return
        
        if self.use_watchdog:
            self._start_watchdog()
        else:
            self._start_polling()
    
    def stop(self):
        """停止文件监控"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        if self.polling_watcher:
            self.polling_watcher.stop()
            self.polling_watcher = None
        
        self.logger.info("文件监控已停止")
    
    def _start_watchdog(self):
        """启动watchdog模式"""
        try:
            self.observer = Observer()
            handler = FileChangeHandler(self.callback, self.debounce_seconds)
            
            for path in self.watched_paths:
                if os.path.exists(path):
                    self.observer.schedule(handler, path, recursive=True)
                    self.logger.info(f"Watchdog监控启动: {path}")
            
            self.observer.start()
            self.logger.info("Watchdog文件监控已启动")
            
        except Exception as e:
            self.logger.error(f"启动watchdog监控失败: {e}")
            self.logger.info("切换到轮询模式")
            self.use_watchdog = False
            self._start_polling()
    
    def _start_polling(self):
        """启动轮询模式"""
        self.polling_watcher = PollingWatcher(
            list(self.watched_paths), 
            self.callback, 
            interval=1.0
        )
        self.polling_watcher.start()

    def get_monitored_files(self) -> List[str]:
        """获取当前监控的所有Python文件"""
        files = []
        for path in self.watched_paths:
            path_obj = Path(path)
            if path_obj.is_dir():
                files.extend([str(f) for f in path_obj.rglob("*.py")])
            elif path_obj.is_file() and path_obj.suffix == '.py':
                files.append(str(path_obj))
        return files