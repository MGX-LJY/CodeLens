"""
CodeLens 日志系统统一接口

为CodeLens项目提供简单易用的日志接口，支持结构化日志记录、
异步写入、文件轮转和配置管理。

使用示例:
    from src.logging import get_logger
    
    logger = get_logger(component="FileService")
    logger.info("Operation completed", {"file_count": 10})
"""

import atexit
import os
from typing import Dict, Optional, Any

from .config import LogConfig, get_default_config, set_default_config
from .manager import LogManager
from .rotator import FileRotator

# 全局日志器缓存
_loggers: Dict[str, LogManager] = {}
_default_config: Optional[LogConfig] = None


def initialize_logging(config_path: Optional[str] = None,
                       **config_overrides) -> LogConfig:
    """初始化日志系统
    
    Args:
        config_path: 配置文件路径
        **config_overrides: 配置覆盖参数
        
    Returns:
        日志配置对象
    """
    global _default_config

    # 加载配置
    if config_path:
        _default_config = LogConfig(config_path)
    else:
        _default_config = LogConfig()

    # 应用配置覆盖
    if config_overrides:
        _default_config.update_config(**config_overrides)

    # 设置为全局默认配置
    set_default_config(_default_config)

    # 注册清理函数
    atexit.register(shutdown_logging)

    return _default_config


def get_logger(component: str, operation: str = "default",
               config: Optional[LogConfig] = None) -> LogManager:
    """获取日志器实例
    
    Args:
        component: 组件名称
        operation: 操作名称
        config: 自定义配置，如果为None则使用默认配置
        
    Returns:
        日志管理器实例
    """
    global _default_config

    # 使用指定配置或默认配置
    if config is None:
        if _default_config is None:
            _default_config = initialize_logging()
        config = _default_config

    # 生成日志器键名
    logger_key = f"{component}:{operation}"

    # 检查缓存
    if logger_key not in _loggers:
        _loggers[logger_key] = LogManager(
            config=config,
            component=component,
            operation=operation
        )

    return _loggers[logger_key]


def create_logger(component: str, operation: str = "default",
                  config_path: Optional[str] = None,
                  **config_overrides) -> LogManager:
    """创建新的日志器实例（不使用缓存）
    
    Args:
        component: 组件名称
        operation: 操作名称
        config_path: 配置文件路径
        **config_overrides: 配置覆盖参数
        
    Returns:
        新的日志管理器实例
    """
    # 创建新的配置实例
    if config_path:
        config = LogConfig(config_path)
    else:
        config = LogConfig()

    # 应用配置覆盖
    if config_overrides:
        config.update_config(**config_overrides)

    return LogManager(
        config=config,
        component=component,
        operation=operation
    )


def set_log_level(level: str, component: Optional[str] = None) -> None:
    """设置日志级别
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        component: 组件名称，如果为None则设置全局级别
    """
    global _default_config

    if _default_config is None:
        _default_config = initialize_logging()

    if component:
        _default_config.update_component_level(component, level)
    else:
        _default_config.update_config(level=level)


def create_default_config_file(config_path: str) -> None:
    """创建默认配置文件
    
    Args:
        config_path: 配置文件路径
    """
    LogConfig.create_default_config_file(config_path)


def get_log_stats() -> Dict[str, Any]:
    """获取日志系统统计信息
    
    Returns:
        统计信息字典
    """
    stats = {
        "active_loggers": len(_loggers),
        "logger_list": list(_loggers.keys()),
        "config": _default_config.to_dict() if _default_config else None,
        "loggers": {}
    }

    # 获取每个日志器的统计信息
    for key, logger in _loggers.items():
        try:
            stats["loggers"][key] = logger.get_stats()
        except Exception as e:
            stats["loggers"][key] = {"error": str(e)}

    return stats


def shutdown_logging(timeout: float = 5.0) -> None:
    """关闭日志系统
    
    Args:
        timeout: 等待超时时间
    """
    global _loggers

    # 关闭所有日志器
    for logger in _loggers.values():
        try:
            logger.shutdown(timeout)
        except Exception as e:
            print(f"Error shutting down logger: {e}")

    # 清空缓存
    _loggers.clear()


def setup_file_logging(log_path: str, level: str = "INFO",
                       max_size_mb: int = 10, backup_count: int = 5) -> LogConfig:
    """快速设置文件日志
    
    Args:
        log_path: 日志文件路径
        level: 日志级别
        max_size_mb: 最大文件大小（MB）
        backup_count: 备份文件数量
        
    Returns:
        配置对象
    """
    config = LogConfig()
    config.update_config(
        level=level,
        file={
            "enabled": True,
            "path": log_path,
            "max_size_mb": max_size_mb,
            "backup_count": backup_count,
            "rotation": "size"
        }
    )

    global _default_config
    _default_config = config
    set_default_config(config)

    return config


def setup_console_logging(level: str = "WARNING") -> LogConfig:
    """快速设置控制台日志
    
    Args:
        level: 控制台日志级别
        
    Returns:
        配置对象
    """
    config = LogConfig()
    config.update_config(
        console={
            "enabled": True,
            "level": level
        },
        file={
            "enabled": False
        }
    )

    global _default_config
    _default_config = config
    set_default_config(config)

    return config


# 便捷函数：使用默认日志器记录日志
def debug(message: str, context: Optional[Dict[str, Any]] = None,
          component: str = "System") -> None:
    """记录DEBUG级别日志"""
    logger = get_logger(component)
    logger.debug(message, context)


def info(message: str, context: Optional[Dict[str, Any]] = None,
         component: str = "System") -> None:
    """记录INFO级别日志"""
    logger = get_logger(component)
    logger.info(message, context)


def warning(message: str, context: Optional[Dict[str, Any]] = None,
            component: str = "System") -> None:
    """记录WARNING级别日志"""
    logger = get_logger(component)
    logger.warning(message, context)


def error(message: str, context: Optional[Dict[str, Any]] = None,
          exc_info: Optional[Exception] = None, component: str = "System") -> None:
    """记录ERROR级别日志"""
    logger = get_logger(component)
    logger.error(message, context, exc_info)


def critical(message: str, context: Optional[Dict[str, Any]] = None,
             exc_info: Optional[Exception] = None, component: str = "System") -> None:
    """记录CRITICAL级别日志"""
    logger = get_logger(component)
    logger.critical(message, context, exc_info)


# 导出主要接口
__all__ = [
    # 核心类
    "LogConfig",
    "LogManager",
    "FileRotator",

    # 初始化和配置
    "initialize_logging",
    "create_default_config_file",
    "setup_file_logging",
    "setup_console_logging",

    # 日志器管理
    "get_logger",
    "create_logger",
    "set_log_level",

    # 便捷日志函数
    "debug",
    "info",
    "warning",
    "error",
    "critical",

    # 系统管理
    "get_log_stats",
    "shutdown_logging"
]


# 自动初始化默认配置（可选）
def _auto_initialize():
    """自动初始化日志系统（如果需要）"""
    # 检查环境变量
    config_path = os.environ.get("CODELENS_LOG_CONFIG")
    log_level = os.environ.get("CODELENS_LOG_LEVEL", "INFO")

    if config_path and os.path.exists(config_path):
        initialize_logging(config_path)
    else:
        # 使用默认配置
        initialize_logging(level=log_level)


# 如果环境变量指定了配置，则自动初始化
if os.environ.get("CODELENS_AUTO_INIT_LOGGING", "false").lower() == "true":
    _auto_initialize()
