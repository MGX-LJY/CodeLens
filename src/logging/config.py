"""
LogConfig - 日志系统配置管理器

为CodeLens日志系统提供配置管理功能，支持从配置文件加载设置、
提供默认配置、运行时配置更新和配置验证。
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class FileConfig:
    """文件日志配置"""
    enabled: bool = True
    path: str = "logs/codelens.log"
    max_size_mb: int = 10
    backup_count: int = 5
    rotation: str = "size"  # "size" 或 "time"


@dataclass
class ConsoleConfig:
    """控制台日志配置"""
    enabled: bool = True
    level: str = "WARNING"


@dataclass
class RetentionConfig:
    """日志保留策略配置"""
    days: int = 30
    compress: bool = True


@dataclass
class LoggingConfig:
    """日志系统主配置"""
    level: str = "INFO"
    format: str = "structured"
    async_enabled: bool = True
    file: FileConfig = None
    console: ConsoleConfig = None
    components: Dict[str, str] = None
    retention: RetentionConfig = None
    
    def __post_init__(self):
        if self.file is None:
            self.file = FileConfig()
        if self.console is None:
            self.console = ConsoleConfig()
        if self.components is None:
            self.components = {
                "FileService": "INFO",
                "TemplateService": "INFO",
                "ValidationService": "INFO",
                "MCP_Tools": "DEBUG"
            }
        if self.retention is None:
            self.retention = RetentionConfig()


class LogConfig:
    """日志配置管理器
    
    职责：
    - 从配置文件加载设置
    - 运行时配置更新
    - 默认配置提供
    - 配置验证
    """
    
    # 有效的日志级别
    VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    
    # 有效的轮转策略
    VALID_ROTATION = {"size", "time"}
    
    # 有效的格式
    VALID_FORMATS = {"structured", "simple"}
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认配置
        """
        self.config_path = config_path
        self._config = LoggingConfig()
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    if "logging" in config_data:
                        config_data = config_data["logging"]
                    self._parse_config(config_data)
            except (json.JSONDecodeError, IOError) as e:
                # 配置文件有问题时使用默认配置
                print(f"Warning: Failed to load config from {self.config_path}: {e}")
                print("Using default configuration.")
        
        # 验证配置
        self._validate_config()
    
    def _parse_config(self, config_data: Dict[str, Any]) -> None:
        """解析配置数据"""
        # 基础配置
        if "level" in config_data:
            self._config.level = config_data["level"]
        if "format" in config_data:
            self._config.format = config_data["format"]
        if "async" in config_data:
            self._config.async_enabled = config_data["async"]
        
        # 文件配置
        if "file" in config_data:
            file_config = config_data["file"]
            self._config.file = FileConfig(
                enabled=file_config.get("enabled", True),
                path=file_config.get("path", "logs/codelens.log"),
                max_size_mb=file_config.get("max_size_mb", 10),
                backup_count=file_config.get("backup_count", 5),
                rotation=file_config.get("rotation", "size")
            )
        
        # 控制台配置
        if "console" in config_data:
            console_config = config_data["console"]
            self._config.console = ConsoleConfig(
                enabled=console_config.get("enabled", True),
                level=console_config.get("level", "WARNING")
            )
        
        # 组件配置
        if "components" in config_data:
            self._config.components.update(config_data["components"])
        
        # 保留策略配置
        if "retention" in config_data:
            retention_config = config_data["retention"]
            self._config.retention = RetentionConfig(
                days=retention_config.get("days", 30),
                compress=retention_config.get("compress", True)
            )
    
    def _validate_config(self) -> None:
        """验证配置有效性"""
        # 验证日志级别
        if self._config.level not in self.VALID_LEVELS:
            raise ValueError(f"Invalid log level: {self._config.level}")
        
        if self._config.console.level not in self.VALID_LEVELS:
            raise ValueError(f"Invalid console log level: {self._config.console.level}")
        
        # 验证格式
        if self._config.format not in self.VALID_FORMATS:
            raise ValueError(f"Invalid log format: {self._config.format}")
        
        # 验证轮转策略
        if self._config.file.rotation not in self.VALID_ROTATION:
            raise ValueError(f"Invalid rotation strategy: {self._config.file.rotation}")
        
        # 验证文件大小和备份数量
        if self._config.file.max_size_mb <= 0:
            raise ValueError("File max_size_mb must be positive")
        
        if self._config.file.backup_count < 0:
            raise ValueError("File backup_count must be non-negative")
        
        # 验证保留天数
        if self._config.retention.days <= 0:
            raise ValueError("Retention days must be positive")
        
        # 验证组件级别
        for component, level in self._config.components.items():
            if level not in self.VALID_LEVELS:
                raise ValueError(f"Invalid level for component {component}: {level}")
    
    def get_config(self) -> LoggingConfig:
        """获取当前配置"""
        return self._config
    
    def get_log_level(self, component: Optional[str] = None) -> str:
        """获取日志级别
        
        Args:
            component: 组件名称，如果指定则返回组件特定级别
            
        Returns:
            日志级别字符串
        """
        if component and component in self._config.components:
            return self._config.components[component]
        return self._config.level
    
    def get_log_level_int(self, component: Optional[str] = None) -> int:
        """获取日志级别的数值表示
        
        Args:
            component: 组件名称
            
        Returns:
            日志级别数值
        """
        level_map = {
            "CRITICAL": 50,
            "ERROR": 40,
            "WARNING": 30,
            "INFO": 20,
            "DEBUG": 10
        }
        level = self.get_log_level(component)
        return level_map.get(level, 20)  # 默认INFO级别
    
    def get_file_path(self) -> str:
        """获取日志文件路径"""
        return self._config.file.path
    
    def get_absolute_file_path(self) -> Path:
        """获取日志文件的绝对路径"""
        file_path = Path(self._config.file.path)
        if not file_path.is_absolute():
            # 相对于项目根目录
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent
            file_path = project_root / file_path
        return file_path
    
    def is_file_logging_enabled(self) -> bool:
        """检查文件日志是否启用"""
        return self._config.file.enabled
    
    def is_console_logging_enabled(self) -> bool:
        """检查控制台日志是否启用"""
        return self._config.console.enabled
    
    def is_async_enabled(self) -> bool:
        """检查异步日志是否启用"""
        return self._config.async_enabled
    
    def update_config(self, **kwargs) -> None:
        """运行时更新配置
        
        Args:
            **kwargs: 要更新的配置项
        """
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                if key == "file" and isinstance(value, dict):
                    # 更新文件配置
                    current_file = self._config.file
                    self._config.file = FileConfig(
                        enabled=value.get("enabled", current_file.enabled),
                        path=value.get("path", current_file.path),
                        max_size_mb=value.get("max_size_mb", current_file.max_size_mb),
                        backup_count=value.get("backup_count", current_file.backup_count),
                        rotation=value.get("rotation", current_file.rotation)
                    )
                elif key == "console" and isinstance(value, dict):
                    # 更新控制台配置
                    current_console = self._config.console
                    self._config.console = ConsoleConfig(
                        enabled=value.get("enabled", current_console.enabled),
                        level=value.get("level", current_console.level)
                    )
                elif key == "retention" and isinstance(value, dict):
                    # 更新保留策略配置
                    current_retention = self._config.retention
                    self._config.retention = RetentionConfig(
                        days=value.get("days", current_retention.days),
                        compress=value.get("compress", current_retention.compress)
                    )
                else:
                    setattr(self._config, key, value)
        
        # 重新验证配置
        self._validate_config()
    
    def update_component_level(self, component: str, level: str) -> None:
        """更新组件日志级别
        
        Args:
            component: 组件名称
            level: 新的日志级别
        """
        if level not in self.VALID_LEVELS:
            raise ValueError(f"Invalid log level: {level}")
        
        self._config.components[component] = level
    
    def save_config(self, config_path: Optional[str] = None) -> None:
        """保存当前配置到文件
        
        Args:
            config_path: 配置文件路径，如果为None则使用初始化时的路径
        """
        save_path = config_path or self.config_path
        if not save_path:
            raise ValueError("No config path specified")
        
        # 确保目录存在
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 构建配置数据
        config_dict = {
            "version": "1.0",
            "logging": {
                "level": self._config.level,
                "format": self._config.format,
                "async": self._config.async_enabled,
                "file": asdict(self._config.file),
                "console": asdict(self._config.console),
                "components": self._config.components,
                "retention": asdict(self._config.retention)
            }
        }
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典"""
        return {
            "level": self._config.level,
            "format": self._config.format,
            "async": self._config.async_enabled,
            "file": asdict(self._config.file),
            "console": asdict(self._config.console),
            "components": self._config.components,
            "retention": asdict(self._config.retention)
        }
    
    @classmethod
    def create_default_config_file(cls, config_path: str) -> None:
        """创建默认配置文件
        
        Args:
            config_path: 配置文件路径
        """
        default_config = cls()
        default_config.save_config(config_path)


# 全局默认配置实例
_default_config = None


def get_default_config() -> LogConfig:
    """获取全局默认配置实例"""
    global _default_config
    if _default_config is None:
        _default_config = LogConfig()
    return _default_config


def set_default_config(config: LogConfig) -> None:
    """设置全局默认配置实例"""
    global _default_config
    _default_config = config