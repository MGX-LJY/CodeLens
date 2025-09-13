"""
LogManager - 日志核心管理器

为CodeLens日志系统提供统一的日志管理功能，包括结构化日志生成、
异步写入、文件轮转协调和上下文信息管理。
"""

import datetime
import json
import os
import sys
import threading
import traceback
import uuid
from queue import Queue, Empty
from typing import Dict, Any, Optional

from .config import LogConfig
from .rotator import FileRotator


class LogRecord:
    """日志记录对象"""

    def __init__(self, level: str, component: str, operation: str,
                 message: str, context: Optional[Dict[str, Any]] = None,
                 exc_info: Optional[Exception] = None):
        self.timestamp = datetime.datetime.now().isoformat() + 'Z'
        self.level = level
        self.component = component
        self.operation = operation
        self.message = message
        self.context = context or {}
        self.exc_info = exc_info

        # 系统元数据
        self.metadata = {
            "pid": os.getpid(),
            "thread_id": threading.current_thread().name,
            "request_id": str(uuid.uuid4())[:8]
        }

    def to_json(self) -> str:
        """转换为JSON字符串"""
        record_dict = {
            "timestamp": self.timestamp,
            "level": self.level,
            "component": self.component,
            "operation": self.operation,
            "message": self.message,
            "context": self.context,
            "metadata": self.metadata
        }

        # 添加异常信息
        if self.exc_info:
            record_dict["exception"] = {
                "type": type(self.exc_info).__name__,
                "message": str(self.exc_info),
                "traceback": traceback.format_exception(
                    type(self.exc_info), self.exc_info, self.exc_info.__traceback__
                )
            }

        return json.dumps(record_dict, ensure_ascii=False, separators=(',', ':'))

    def to_simple(self) -> str:
        """转换为简单格式字符串"""
        parts = [
            self.timestamp,
            f"[{self.level}]",
            f"[{self.component}]",
            f"[{self.operation}]",
            self.message
        ]

        if self.context:
            context_str = json.dumps(self.context, ensure_ascii=False)
            parts.append(f"context={context_str}")

        if self.exc_info:
            parts.append(f"error={str(self.exc_info)}")

        return " ".join(parts)


class AsyncLogWriter:
    """异步日志写入器"""

    def __init__(self, config: LogConfig):
        self.config = config
        self.log_queue = Queue()
        self.rotator = FileRotator(config)
        self.worker_thread = None
        self.shutdown_flag = threading.Event()
        self.file_handle = None

        if config.is_async_enabled():
            self._start_worker()

    def _start_worker(self) -> None:
        """启动后台写入线程"""
        self.worker_thread = threading.Thread(
            target=self._worker_loop,
            name="LogWriter",
            daemon=True
        )
        self.worker_thread.start()

    def _worker_loop(self) -> None:
        """后台线程工作循环"""
        while not self.shutdown_flag.is_set():
            try:
                # 从队列获取日志记录，超时1秒
                record = self.log_queue.get(timeout=1.0)
                if record is None:  # 停止信号
                    break

                self._write_record(record)
                self.log_queue.task_done()

            except Empty:
                continue
            except Exception as e:
                print(f"Error in log writer: {e}", file=sys.stderr)

    def _write_record(self, record: LogRecord) -> None:
        """写入日志记录到文件"""
        if not self.config.is_file_logging_enabled():
            return

        try:
            # 检查是否需要轮转
            if self.rotator.should_rotate():
                self._close_file()
                self.rotator.rotate_file()

            # 确保文件句柄存在
            if self.file_handle is None:
                self._open_file()

            # 写入日志
            if self.file_handle:
                log_format = self.config.get_config().format
                if log_format == "structured":
                    line = record.to_json()
                else:
                    line = record.to_simple()

                self.file_handle.write(line + '\n')
                self.file_handle.flush()

        except Exception as e:
            print(f"Error writing log record: {e}", file=sys.stderr)

    def _open_file(self) -> None:
        """打开日志文件"""
        try:
            log_path = self.config.get_absolute_file_path()
            self.file_handle = open(log_path, 'a', encoding='utf-8')
        except Exception as e:
            print(f"Error opening log file: {e}", file=sys.stderr)

    def _close_file(self) -> None:
        """关闭日志文件"""
        if self.file_handle:
            try:
                self.file_handle.close()
            except Exception:
                pass
            finally:
                self.file_handle = None

    def write_sync(self, record: LogRecord) -> None:
        """同步写入日志记录"""
        self._write_record(record)

    def write_async(self, record: LogRecord) -> None:
        """异步写入日志记录"""
        if self.worker_thread and self.worker_thread.is_alive():
            try:
                self.log_queue.put_nowait(record)
            except Exception as e:
                print(f"Error queuing log record: {e}", file=sys.stderr)
                # 队列满时回退到同步写入
                self.write_sync(record)
        else:
            # 异步线程不可用时使用同步写入
            self.write_sync(record)

    def shutdown(self, timeout: float = 5.0) -> None:
        """关闭写入器"""
        if self.worker_thread and self.worker_thread.is_alive():
            # 发送停止信号
            self.shutdown_flag.set()
            try:
                self.log_queue.put_nowait(None)
            except Exception:
                pass

            # 等待线程结束
            self.worker_thread.join(timeout)

        self._close_file()


class LogManager:
    """日志核心管理器
    
    职责：
    - 统一的日志入口，管理所有日志操作
    - 生成结构化的JSON格式日志
    - 标准化日志消息格式
    - 自动添加时间戳、级别、模块信息
    - 支持嵌套对象和复杂数据结构
    - 异常信息格式化
    - 协调异步日志写入
    - 上下文信息收集和注入
    """

    # 日志级别映射
    LEVEL_MAP = {
        "CRITICAL": 50,
        "ERROR": 40,
        "WARNING": 30,
        "INFO": 20,
        "DEBUG": 10
    }

    def __init__(self, config: LogConfig, component: str = "System",
                 operation: str = "default"):
        """初始化日志管理器
        
        Args:
            config: 日志配置对象
            component: 组件名称
            operation: 操作名称
        """
        self.config = config
        self.component = component
        self.operation = operation
        self.context = {}

        # 初始化异步写入器
        self.writer = AsyncLogWriter(config)

        # 控制台输出配置
        self.console_enabled = config.is_console_logging_enabled()
        self.console_level = config.get_log_level_int()

    def set_context(self, **context) -> None:
        """设置日志上下文
        
        Args:
            **context: 上下文键值对
        """
        self.context.update(context)

    def clear_context(self) -> None:
        """清空日志上下文"""
        self.context.clear()

    def _should_log(self, level: str) -> bool:
        """检查是否应该记录此级别的日志
        
        Args:
            level: 日志级别
            
        Returns:
            是否应该记录
        """
        current_level = self.config.get_log_level_int(self.component)
        record_level = self.LEVEL_MAP.get(level, 20)

        return record_level >= current_level

    def _create_record(self, level: str, message: str,
                       context: Optional[Dict[str, Any]] = None,
                       exc_info: Optional[Exception] = None) -> LogRecord:
        """创建日志记录
        
        Args:
            level: 日志级别
            message: 日志消息
            context: 附加上下文
            exc_info: 异常信息
            
        Returns:
            日志记录对象
        """
        # 合并上下文
        merged_context = self.context.copy()
        if context:
            merged_context.update(context)

        return LogRecord(
            level=level,
            component=self.component,
            operation=self.operation,
            message=message,
            context=merged_context,
            exc_info=exc_info
        )

    def _output_to_console(self, record: LogRecord) -> None:
        """输出日志到控制台
        
        Args:
            record: 日志记录
        """
        if not self.console_enabled:
            return

        console_config = self.config.get_config().console
        console_level = self.LEVEL_MAP.get(console_config.level, 30)
        record_level = self.LEVEL_MAP.get(record.level, 20)

        if record_level >= console_level:
            output = record.to_simple() if self.config.get_config().format == "simple" else record.to_json()
            print(output, file=sys.stderr)

    def _log(self, level: str, message: str,
             context: Optional[Dict[str, Any]] = None,
             exc_info: Optional[Exception] = None) -> None:
        """内部日志记录方法
        
        Args:
            level: 日志级别
            message: 日志消息
            context: 附加上下文
            exc_info: 异常信息
        """
        if not self._should_log(level):
            return

        # 创建日志记录
        record = self._create_record(level, message, context, exc_info)

        # 输出到控制台
        self._output_to_console(record)

        # 写入文件
        if self.config.is_file_logging_enabled():
            if self.config.is_async_enabled():
                self.writer.write_async(record)
            else:
                self.writer.write_sync(record)

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """记录DEBUG级别日志
        
        Args:
            message: 日志消息
            context: 附加上下文
        """
        self._log("DEBUG", message, context)

    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """记录INFO级别日志
        
        Args:
            message: 日志消息
            context: 附加上下文
        """
        self._log("INFO", message, context)

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """记录WARNING级别日志
        
        Args:
            message: 日志消息
            context: 附加上下文
        """
        self._log("WARNING", message, context)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None,
              exc_info: Optional[Exception] = None) -> None:
        """记录ERROR级别日志
        
        Args:
            message: 日志消息
            context: 附加上下文
            exc_info: 异常信息
        """
        self._log("ERROR", message, context, exc_info)

    def critical(self, message: str, context: Optional[Dict[str, Any]] = None,
                 exc_info: Optional[Exception] = None) -> None:
        """记录CRITICAL级别日志
        
        Args:
            message: 日志消息
            context: 附加上下文
            exc_info: 异常信息
        """
        self._log("CRITICAL", message, context, exc_info)

    def log_operation_start(self, operation: str, **context) -> str:
        """记录操作开始
        
        Args:
            operation: 操作名称
            **context: 上下文信息
            
        Returns:
            操作ID
        """
        operation_id = str(uuid.uuid4())[:8]
        self.info(f"Operation started: {operation}", {
            "operation": operation,
            "operation_id": operation_id,
            **context
        })
        return operation_id

    def log_operation_end(self, operation: str, operation_id: str,
                          duration_ms: Optional[float] = None,
                          success: bool = True, **context) -> None:
        """记录操作结束
        
        Args:
            operation: 操作名称
            operation_id: 操作ID
            duration_ms: 操作耗时（毫秒）
            success: 操作是否成功
            **context: 上下文信息
        """
        log_context = {
            "operation": operation,
            "operation_id": operation_id,
            "success": success,
            **context
        }

        if duration_ms is not None:
            log_context["duration_ms"] = duration_ms

        level = "info" if success else "error"
        message = f"Operation completed: {operation}" if success else f"Operation failed: {operation}"

        getattr(self, level)(message, log_context)

    def create_child_logger(self, component: str, operation: str = None) -> 'LogManager':
        """创建子日志器
        
        Args:
            component: 组件名称
            operation: 操作名称
            
        Returns:
            子日志器
        """
        child_logger = LogManager(
            config=self.config,
            component=component,
            operation=operation or self.operation
        )

        # 继承父级上下文
        child_logger.context = self.context.copy()

        return child_logger

    def get_stats(self) -> Dict[str, Any]:
        """获取日志统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            "component": self.component,
            "operation": self.operation,
            "config": self.config.to_dict(),
            "queue_size": 0,
            "file_info": {}
        }

        # 队列大小（异步模式）
        if self.config.is_async_enabled() and hasattr(self.writer, 'log_queue'):
            stats["queue_size"] = self.writer.log_queue.qsize()

        # 文件信息
        if hasattr(self.writer, 'rotator'):
            stats["file_info"] = self.writer.rotator.get_disk_usage()

        return stats

    def shutdown(self, timeout: float = 5.0) -> None:
        """关闭日志管理器
        
        Args:
            timeout: 等待超时时间
        """
        if hasattr(self, 'writer'):
            self.writer.shutdown(timeout)
