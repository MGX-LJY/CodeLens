"""
热重载管理器 - 协调文件监控和模块重载的核心组件
"""

import asyncio
import time
from pathlib import Path
from typing import Dict, List, Set, Optional, Callable, Any
from threading import Lock
from collections import defaultdict
import weakref

from .file_watcher import FileWatcher
from .module_reloader import ModuleReloader
from src.logging import get_logger

class ReloadEvent:
    """重载事件"""
    
    def __init__(self, file_path: str, module_name: str, timestamp: float):
        self.file_path = file_path
        self.module_name = module_name
        self.timestamp = timestamp
        self.success: Optional[bool] = None
        self.error: Optional[str] = None

class HotReloadManager:
    """热重载管理器"""
    
    def __init__(self, 
                 enabled: bool = True,
                 debounce_seconds: float = 0.5,
                 batch_reload_window: float = 2.0):
        """
        初始化热重载管理器
        
        Args:
            enabled: 是否启用热重载
            debounce_seconds: 文件变化防抖动时间
            batch_reload_window: 批量重载时间窗口
        """
        self.enabled = enabled
        self.debounce_seconds = debounce_seconds
        self.batch_reload_window = batch_reload_window
        
        # 核心组件
        self.file_watcher = FileWatcher(
            callback=self._on_file_changed,
            debounce_seconds=debounce_seconds
        )
        self.module_reloader = ModuleReloader()
        
        # 状态管理
        self.is_running = False
        self.pending_reloads: Dict[str, ReloadEvent] = {}
        self.reload_history: List[ReloadEvent] = []
        self.lock = Lock()
        
        # 回调函数
        self.reload_callbacks: List[Callable[[ReloadEvent], None]] = []
        self.tool_instances: Dict[str, Any] = {}  # 工具实例缓存
        
        # 批量重载任务
        self._batch_reload_task: Optional[asyncio.Task] = None
        
        self.logger = get_logger("HotReloadManager", "hot_reload_coordination")
        
        # 自动添加项目监控路径
        self._setup_default_watch_paths()
    
    def _setup_default_watch_paths(self):
        """设置默认的监控路径"""
        project_root = Path(__file__).parent.parent.parent
        watch_paths = [
            project_root / "src" / "mcp_tools",
            project_root / "src" / "services", 
            project_root / "src" / "task_engine",
            project_root / "src" / "templates",
            project_root / "src" / "logging",
            project_root / "src" / "hot_reload"
        ]
        
        for path in watch_paths:
            if path.exists():
                self.file_watcher.add_path(str(path))
                self.logger.debug(f"添加默认监控路径: {path}")
    
    def register_tool_instance(self, tool_name: str, instance: Any):
        """注册工具实例，以便在重载后更新"""
        self.tool_instances[tool_name] = weakref.ref(instance)
        self.logger.debug(f"注册工具实例: {tool_name}")
    
    def add_reload_callback(self, callback: Callable[[ReloadEvent], None]):
        """添加重载回调函数"""
        self.reload_callbacks.append(callback)
    
    def start(self):
        """启动热重载管理器"""
        if not self.enabled:
            self.logger.info("热重载已禁用")
            return
        
        if self.is_running:
            self.logger.warning("热重载管理器已在运行")
            return
        
        try:
            self.file_watcher.start()
            self.is_running = True
            self.logger.info("🔥 热重载管理器启动成功")
            
            # 显示监控信息
            monitored_files = self.file_watcher.get_monitored_files()
            self.logger.info(f"监控 {len(monitored_files)} 个Python文件")
            
        except Exception as e:
            self.logger.error(f"启动热重载管理器失败: {e}")
            raise
    
    def stop(self):
        """停止热重载管理器"""
        if not self.is_running:
            return
        
        try:
            self.file_watcher.stop()
            
            # 取消批量重载任务
            if self._batch_reload_task and not self._batch_reload_task.done():
                self._batch_reload_task.cancel()
            
            self.is_running = False
            self.logger.info("热重载管理器已停止")
            
        except Exception as e:
            self.logger.error(f"停止热重载管理器失败: {e}")
    
    def _on_file_changed(self, file_path: str):
        """文件变化回调"""
        if not self.enabled or not self.is_running:
            return
        
        try:
            module_name = self.module_reloader.file_path_to_module_name(file_path)
            if not module_name:
                return
            
            if not self.module_reloader.is_reloadable(module_name):
                self.logger.debug(f"模块不可重载，跳过: {module_name}")
                return
            
            # 创建重载事件
            reload_event = ReloadEvent(file_path, module_name, time.time())
            
            with self.lock:
                self.pending_reloads[module_name] = reload_event
            
            self.logger.info(f"文件变化触发重载: {file_path} -> {module_name}")
            
            # 启动批量重载
            self._schedule_batch_reload()
            
        except Exception as e:
            self.logger.error(f"处理文件变化事件失败: {file_path}, 错误: {e}")
    
    def _schedule_batch_reload(self):
        """调度批量重载"""
        try:
            # 如果已有批量重载任务在运行，取消它
            if self._batch_reload_task and not self._batch_reload_task.done():
                self._batch_reload_task.cancel()
            
            # 创建新的批量重载任务
            loop = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # 没有运行的事件循环，在新线程中处理
                import threading
                thread = threading.Thread(target=self._perform_batch_reload, daemon=True)
                thread.start()
                return
            
            # 在现有事件循环中调度
            self._batch_reload_task = loop.create_task(self._async_batch_reload())
            
        except Exception as e:
            self.logger.error(f"调度批量重载失败: {e}")
    
    async def _async_batch_reload(self):
        """异步批量重载"""
        try:
            await asyncio.sleep(self.batch_reload_window)
            self._perform_batch_reload()
        except asyncio.CancelledError:
            self.logger.debug("批量重载任务被取消")
        except Exception as e:
            self.logger.error(f"异步批量重载失败: {e}")
    
    def _perform_batch_reload(self):
        """执行批量重载"""
        with self.lock:
            if not self.pending_reloads:
                return
            
            events_to_process = dict(self.pending_reloads)
            self.pending_reloads.clear()
        
        self.logger.info(f"开始批量重载 {len(events_to_process)} 个模块")
        
        # 按依赖顺序重载
        reload_order = self._calculate_reload_order(list(events_to_process.keys()))
        
        for module_name in reload_order:
            if module_name in events_to_process:
                event = events_to_process[module_name]
                self._reload_module(event)
        
        # 通知工具实例更新
        self._update_tool_instances(list(events_to_process.keys()))
        
        self.logger.info("批量重载完成")
    
    def _calculate_reload_order(self, module_names: List[str]) -> List[str]:
        """计算重载顺序"""
        # 简化版：按模块层级排序（深层模块先重载）
        def module_depth(name: str) -> int:
            return name.count('.')
        
        return sorted(module_names, key=module_depth, reverse=True)
    
    def _reload_module(self, event: ReloadEvent):
        """重载单个模块"""
        start_time = time.time()
        
        try:
            self.logger.info(f"重载模块: {event.module_name}")
            
            # 清除模块缓存
            self.module_reloader.clear_module_cache(event.module_name)
            
            # 执行重载
            success = self.module_reloader.reload_module(event.module_name)
            
            event.success = success
            event.error = None if success else "重载失败"
            
            duration = time.time() - start_time
            
            if success:
                self.logger.info(f"✅ 模块重载成功: {event.module_name} ({duration:.2f}s)")
            else:
                self.logger.error(f"❌ 模块重载失败: {event.module_name}")
            
        except Exception as e:
            event.success = False
            event.error = str(e)
            self.logger.error(f"❌ 模块重载异常: {event.module_name}, 错误: {e}")
        
        # 记录到历史
        with self.lock:
            self.reload_history.append(event)
            # 保持历史记录不超过100条
            if len(self.reload_history) > 100:
                self.reload_history = self.reload_history[-100:]
        
        # 调用回调函数
        for callback in self.reload_callbacks:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"执行重载回调失败: {e}")
    
    def _update_tool_instances(self, reloaded_modules: List[str]):
        """更新工具实例"""
        try:
            # 这里可以实现更复杂的工具实例更新逻辑
            # 目前只是记录日志
            if reloaded_modules:
                self.logger.info(f"需要更新的工具实例关联模块: {', '.join(reloaded_modules)}")
            
            # 清理失效的弱引用
            dead_refs = []
            for name, ref in self.tool_instances.items():
                if ref() is None:
                    dead_refs.append(name)
            
            for name in dead_refs:
                del self.tool_instances[name]
                
        except Exception as e:
            self.logger.error(f"更新工具实例失败: {e}")
    
    def force_reload_all(self) -> Dict[str, bool]:
        """强制重载所有项目模块"""
        self.logger.info("强制重载所有项目模块")
        return self.module_reloader.reload_all_project_modules()
    
    def get_status(self) -> Dict[str, Any]:
        """获取热重载状态"""
        with self.lock:
            pending_count = len(self.pending_reloads)
            recent_reloads = [
                {
                    'module': event.module_name,
                    'timestamp': event.timestamp,
                    'success': event.success,
                    'error': event.error
                }
                for event in self.reload_history[-10:]
            ]
        
        monitored_files = []
        if self.is_running:
            monitored_files = self.file_watcher.get_monitored_files()
        
        return {
            'enabled': self.enabled,
            'running': self.is_running,
            'pending_reloads': pending_count,
            'monitored_files_count': len(monitored_files),
            'recent_reloads': recent_reloads,
            'tool_instances_count': len([ref for ref in self.tool_instances.values() if ref() is not None])
        }
    
    def add_watch_path(self, path: str):
        """添加监控路径"""
        self.file_watcher.add_path(path)
        self.logger.info(f"添加监控路径: {path}")
    
    def enable(self):
        """启用热重载"""
        self.enabled = True
        self.logger.info("热重载已启用")
    
    def disable(self):
        """禁用热重载"""
        self.enabled = False
        self.logger.info("热重载已禁用")
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()